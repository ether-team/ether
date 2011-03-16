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

"""SVN hooks API."""

import os

from ether.hookman.common import HookAPI, HookError
from ConfigParser import ConfigParser

class HgHookAPI(HookAPI):
    """API for maintaining mercurial hooks."""

    def __init__(self, basedir='/usr/share/vcs-hooks/hg'):
        HookAPI.__init__(self, basedir,
                         hook_names = ("changegroup", "commit",
                                       "incoming", "outgoing", "prechangegroup",
                                       "precommit", "preoutgoing", "pretag",
                                       "pretxnchangegroup", "pretxncommit",
                                       "preupdate", "tag", "update"))

    def get_hook_path(self, repo, hook_name):
        return os.path.join(repo, ".hg", "hooks", hook_name)

    def setup(self, repo, hook):
        """Setup hook infrastructure.
           In addition to common things it also updates .hg/hgrc."""

        HookAPI.setup(self, repo, hook)
        rc_path = os.path.join(repo, ".hg", "hgrc")

        parser = ConfigParser()

        if os.path.exists(rc_path):
            parser.read([rc_path])

        section = "hooks"
        if not parser.has_section(section):
            parser.add_section(section)

        hook_path = self.hook_path(repo, hook)
        if parser.has_option(section, hook):
            if parser.get(section, hook) != hook_path:
                raise HookError("%s: %s hook is already set" % (rc_path, hook))
        else:
            parser.set(section, hook, hook_path)

        with open(rc_path, "w") as fhandle:
            parser.write(fhandle)

    def teardown(self, repo, hook):
        """Remove hooks infrastructure."""

        rc_path = os.path.join(repo, ".hg", "hgrc")

        if not os.path.exists(rc_path):
            return

        if HookAPI.teardown(self, repo, hook):
            parser = ConfigParser()
            parser.read([rc_path])
            section = 'hooks'
            if parser.has_option(section, hook) and  \
                   parser.get(section, hook) == self.hook_path(repo, hook):
                parser.remove_option(section, hook)
                return True

# vim: sw=4 ts=4 expandtab ai
