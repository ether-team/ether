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

"""Tests for hooks API."""

import os
import stat
import unittest
import shutil
import tempfile

from ConfigParser import ConfigParser

from ether.hookman.common import HookError, HookAPI
from ether.hookman.svn import SvnHookAPI
from ether.hookman.git import GitHookAPI
from ether.hookman.hg import HgHookAPI

class HooksAPITest(unittest.TestCase):
    """VCS hook test sute."""

    @staticmethod
    def create_hook(fpath):
        """Helper. Create hook script."""
        dirname = os.path.dirname(fpath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(fpath, "w") as fileo:
            fileo.write("#!/bin/sh")
        os.chmod(fpath, stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR)

    def setUp(self):
        """Setup fixture."""

        self.root = tempfile.mkdtemp()
        basedir = os.path.join(self.root, "base")
        os.makedirs(basedir)
        for name in ("hook1", "hook2"):
            hpath = os.path.join(basedir, name)
            self.create_hook(hpath)

        # svn
        self.svnrepo = os.path.join(self.root, "svnrepo")
        self.svnapi = SvnHookAPI(basedir)
        self.svnhooks = self.svnapi.hook_names
        svnhookdir = os.path.join(self.svnrepo, "hooks")
        os.makedirs(svnhookdir)
        presethook = os.path.join(svnhookdir, self.svnhooks[2])
        self.create_hook(presethook)
        for hook_name in self.svnhooks:
            self.svnapi.setup(self.svnrepo, hook_name)

        existinghook = os.path.join(self.svnapi.hook_path(self.svnrepo,
                                    self.svnhooks[2])+'.d', self.svnhooks[2])
        self.create_hook(existinghook)

        # git
        self.gitrepo = os.path.join(self.root, "gitrepo")
        self.gitapi = GitHookAPI(self.gitrepo)
        self.githooks = self.gitapi.hook_names
        githookdir = os.path.join(self.gitrepo, ".git", "hooks")
        os.makedirs(githookdir)

        # hg
        self.hgrepo = os.path.join(self.root, "hgrepo")
        self.hgapi = HgHookAPI(self.hgrepo)
        self.hghooks = self.hgapi.hook_names
        hghookdir = os.path.join(self.hgrepo, ".hg", "hooks")
        os.makedirs(hghookdir)

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_abstract_class(self):
        class IncompleteHookAPI(HookAPI):
            pass
        self.assertRaises(TypeError, IncompleteHookAPI, "basedir",
                          ["pre-commit", "post-commit"])

    def test_setup(self):
        self.assertRaises(HookError, self.svnapi.setup, self.svnrepo, "bla")
        self.assertRaises(HookError, self.svnapi.hook_path,
                          self.svnrepo, "Unkonwn hook")

        hook = self.svnhooks[2]
        hook_path = self.svnapi.hook_path(self.svnrepo, hook)
        existinghook = os.path.join(hook_path +'.d', hook)

        self.svnapi.teardown(self.svnrepo, hook)
        self.create_hook(existinghook)

        self.assertRaises(HookError, self.svnapi.setup, self.svnrepo, hook)

        self.svnapi.setup(self.svnrepo, self.svnhooks[0])
        self.svnapi.setup(self.svnrepo, self.svnhooks[3])
        self.gitapi.setup(self.gitrepo, self.githooks[0])

    def test_avail(self):
        self.assertEqual(set(self.svnapi.avail()), set(["hook1", "hook2"]))

    def test_add(self):
        self.svnapi.add(self.svnrepo, self.svnhooks[0], "hook1")
        self.assertRaises(HookError, self.svnapi.add, self.svnrepo,
                          self.svnhooks[0], "bla")
        self.assertRaises(HookError, self.svnapi.add, self.svnrepo,
                          self.svnhooks[0], "hook1")
        self.assertEqual(self.svnapi.lst(\
                         self.svnrepo)[self.svnhooks[0]], ['hook1'])

    def test_lst(self):
        self.assertEqual(self.svnapi.lst(self.svnrepo),
                   {self.svnhooks[2]: [self.svnhooks[2]]})
                    #self.svnhooks[3]: [self.svnhooks[3]]})

    def test_remove(self):
        self.assertRaises(HookError, self.svnapi.remove, self.svnrepo,
                          self.svnhooks[1], "hook2")
        self.svnapi.add(self.svnrepo, self.svnhooks[0], "hook1")
        self.svnapi.remove(self.svnrepo, self.svnhooks[0], "hook1")
        self.assertFalse(self.svnhooks[0] \
                             in self.svnapi.lst(self.svnrepo))

    def test_teardown(self):
        self.assertEqual(self.svnapi.teardown(self.svnrepo,
                                              self.svnhooks[1]), True)
        self.assertRaises(HookError, self.svnapi.teardown, self.svnrepo,
                          self.svnhooks[1])
        self.assertEqual(self.svnapi.teardown(self.svnrepo,
                                              self.svnhooks[2]), True)

    def test_hg_setup(self):
        self.hgapi.setup(self.hgrepo, self.hghooks[0])
        parser = ConfigParser()
        hgrc_path = os.path.join(self.hgrepo, ".hg", "hgrc")
        parser.read([hgrc_path])
        parser.set("hooks", self.hghooks[1], "whatever")
        with open(hgrc_path, "w") as hgrc:
            parser.write(hgrc)
        self.assertRaises(HookError, self.hgapi.setup, self.hgrepo,
                          self.hghooks[1])

    def test_hg_teardown(self):
        self.hgapi.setup(self.hgrepo, self.hghooks[0])
        self.assertTrue(self.hgapi.teardown(self.hgrepo, self.hghooks[0]))
        os.unlink(os.path.join(os.path.join(self.hgrepo, ".hg", "hgrc")))
        self.assertEqual(self.hgapi.teardown(self.hgrepo,
                                             self.hghooks[0]), None)

# vim: sw=4 ts=4 expandtab ai
