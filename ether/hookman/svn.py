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

from ether.hookman.common import HookAPI

class SvnHookAPI(HookAPI):
    """API for maintaining svn hooks."""

    def __init__(self, basedir='/usr/share/vcs-hooks/svn'):
        HookAPI.__init__(self, basedir,
                         hook_names = ("post-commit", "post-lock",
                                       "post-revprop-change", "post-unlock",
                                       "pre-commit", "pre-lock",
                                       "pre-revprop-change", "pre-unlock",
                                       "start-commit"))

    def hook_path(self, repo, hook_name):
        HookAPI.hook_path(self, repo, hook_name)
        return os.path.join(repo, "hooks", hook_name)

# vim: sw=4 ts=4 expandtab ai
