#!/usr/bin/python -tt
#
# This file is part of BIFH.
#
# Copyright (C) 2006, 2007, 2008, 2009, 2010 Nokia Corporation and/or its
# subsidiary(-ies).
#
# Contact: BIFH Team <bifh-team@nokia.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA

"""VCS hook manager."""

import sys
import os
import logging
import pkg_resources

from optparse import OptionParser

from bifh.vcs.hooks.common import HookError

CATEGORY = "bifh.vcs.hooks"

APP = os.path.basename(sys.argv[0])
LOG = logging.getLogger(APP)

LOG_FORMAT = "[%(asctime)s] %(name)s [%(levelname)s]: %(message)s"
LOG_DATE_FORMAT  = "%X"

def get_option_parser():
    """Parse command line options."""

    parser = OptionParser(usage="%prog <type> [<hook>] [<repo>] [OPTIONS]",
                          prog=APP)

    parser.add_option('-v', '--avail', action='store_true',
                      help='list available hooks')
    parser.add_option('-a', '--add', help='add hook to the repo')
    parser.add_option('-r', '--remove', help='remove hook from the repo')
    parser.add_option('-l', '--list', action='store_true',
                      help='list repo hooks')

    parser.add_option('-d', '--debug', action='store_true',
                      help='Debug; show debug info')
    return parser


def main():
    """Main entry point."""

    parser = get_option_parser()
    options, args = parser.parse_args(sys.argv)

    # list of available hooks requires only one argument - type
    if options.avail:
        if len(args) < 2:
            parser.print_help()
            return 1
        vcstype = args[1]
    else:
        if len(args) < 4:
            parser.print_help()
            return 1
        vcstype, hook, repo = args[1:4]

    logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    actions = (options.list, options.avail, bool(options.add),
               bool(options.remove)).count(True)
    if actions == 0:
        LOG.error("No action option specified. Use -l -a -r or -v")
        return 1
    elif actions > 1:
        LOG.error("More than one action option specified")
        return 1

    LOG.debug("Start")

    # Check vcs hook API is available
    eps = [ep for ep in pkg_resources.iter_entry_points(CATEGORY) \
            if ep.name == vcstype]
    if not eps:
        LOG.error("%s vcs hook plugin is not installed", vcstype.title())
        return 1
    if len(eps) > 1:
        LOG.error("More than one %s vcs hook plugin is installed",
                  vcstype.title())
        return 1

    api = eps[0].load()()

    try:
        if options.list:
            result = api.lst(repo)
            for name, hooks in result.iteritems():
                print(" %s:" % name)
                print(os.linesep.join(hooks))
        elif options.avail:
            print(os.linesep.join(api.avail()))
        elif options.add:
            api.add(repo, hook, options.add)
        elif options.remove:
            api.remove(repo, hook, options.remove)
    except HookError, exobj:
        LOG.error(exobj)
        return 1

    LOG.debug("End.")
    return 0

if __name__ == '__main__':
    sys.exit(main())

# vim: sw=4 ts=4 expandtab ai
