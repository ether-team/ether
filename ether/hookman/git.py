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

"""Git hooks API."""

import os

from ether.hookman.common import HookAPI

class GitHookAPI(HookAPI):
    """API for maintaining svn hooks."""

    def __init__(self, basedir='/usr/share/vcs-hooks/git'):
        HookAPI.__init__(self, basedir,
                         hook_names = ("applypatch-msg", "pre-applypatch",
                                       "post-applypatch", "pre-commit",
                                       "prepare-commit-msg", "commit-msg",
                                       "post-commit", "pre-rebase",
                                       "post-checkout", "post-merge",
                                       "pre-receive", "update", "post-receive",
                                       "post-update", "pre-auto-gc"))

    def hook_path(self, repo, hook_name):
        HookAPI.hook_path(self, repo, hook_name)
        return os.path.join(repo, ".git/hooks", hook_name)

# vim: sw=4 ts=4 expandtab ai
