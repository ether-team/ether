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

"""Hooks API. Common part."""

import os
import logging

from abc import ABCMeta, abstractmethod

LOG = logging.getLogger(__name__)

class HookError(Exception):
    """Hook exception."""
    pass

class HookAPI(object):
    """Base class for hook APIs."""

    __metaclass__ = ABCMeta

    _root_hook_name = "root_hook.sh"

    def __init__(self, basedir, hook_names):
        self._basedir = basedir
        self._hook_names = hook_names
        self._root_hook = os.path.join(basedir, self._root_hook_name)

    @abstractmethod
    def get_hook_path(self, repo, hook_name):
        """Get path to hook by name."""
        raise NotImplementedError

    def hook_path(self, repo, hook_name):
        """Get path to hook by name.
           Here are only validation of params and call of get_hook_path
        """
        if hook_name not in self._hook_names:
            raise HookError("Unknown hook: %s" % hook_name)
        return self.get_hook_path(repo, hook_name)

    def setup(self, repo, hook):
        """Setup hooks infrastructure if needed."""

        if hook not in self._hook_names:
            raise HookError("Unknown hook: %s" % hook)

        hook_path = self.hook_path(repo, hook)

        LOG.debug("Checking if %s exists and linked to root hook" % hook_path)
        if os.path.islink(hook_path) and \
               os.readlink(hook_path) == self._root_hook:
            return

        hooks_d = hook_path + ".d"
        if not os.path.exists(hooks_d):
            os.mkdir(hooks_d)

        if os.path.exists(hook_path):
            LOG.debug("Moving existing hook %s to %s.d", hook, hook)
            hook_path_new = os.path.join(hooks_d, hook)
            if not os.path.exists(hook_path_new):
                os.rename(hook_path, hook_path_new)
            else:
                raise HookError("Can't move hook %s. Destination path %s "
                                "already exists" % (hook_path, hook_path_new))

        # symlink root hook
        os.symlink(self._root_hook, hook_path)

    def teardown(self, repo, hook):
        """Remove hooks infrastructure if there are no hooks in the repo.
           return True if removes root hook
        """

        hook_path = self.hook_path(repo, hook)
        hooks_d = hook_path + ".d"
        if not os.path.isdir(hooks_d):
            raise HookError("%s does not exist.  Can't teardown the "
                             "infrastructure" % hooks_d)

        files = os.listdir(hooks_d)

        if os.path.islink(hook_path) and \
               os.readlink(hook_path) == self._root_hook:
            if files == [hook]:
                # existed hook was moved to .d in self.setup
                # move it back and remove hooks_d
                os.unlink(hook_path)
                os.rename(os.path.join(hooks_d, hook), hook_path)
                os.rmdir(hooks_d)
                return True
            elif not files:
                # no files left in hooks_d
                # unlink root hook and remove hooks_d
                os.unlink(hook_path)
                os.rmdir(hooks_d)
                return True

    def lst(self, repo):
        """List repo hooks."""
        result = {}
        for hook in self._hook_names:
            hooks_d = self.hook_path(repo, hook) + ".d"
            if os.path.isdir(hooks_d):
                hooks = [path for path in os.listdir(hooks_d) \
                         if os.path.isfile(os.path.join(hooks_d, path))]
                if hooks:
                    result[hook] = hooks[:]
        return result

    def avail(self):
        """List available hooks."""
        return [fname for fname in os.listdir(self._basedir) \
                if os.path.isfile(os.path.join(self._basedir, fname)) \
                and '.' not in fname]


    def add(self, repo, hook, script):
        """Add hook to the repo."""

        src = os.path.join(self._basedir, script)
        if not os.path.isfile(src):
            raise HookError("Hook %s not found" % src)

        hooks_d = self.hook_path(repo, hook) + ".d"
        dst = os.path.join(hooks_d, script)
        if os.path.exists(dst):
            raise HookError("Path %s already exists" % dst)

        self.setup(repo, hook)

        os.symlink(src, dst)

    def remove(self, repo, hook, script):
        """Remove hook from the repo."""

        hooks_d = self.hook_path(repo, hook) + ".d"
        dst = os.path.join(hooks_d, script)
        if not os.path.exists(dst):
            raise HookError("Path %s doesnt exist" % dst)
        os.unlink(dst)
        self.teardown(repo, hook)

# vim: sw=4 ts=4 expandtab ai
