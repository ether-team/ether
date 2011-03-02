import unittest, os, sys

import settings

from ether import fixtures

from ether.hooks import git, svn
from ether.publishers.log import FileLogger

class TPublisher(object):

    def __init__(self):
        self.payload = None

    def send_payload(self, payload):
        self.payload = payload

class TestGitHook(unittest.TestCase):

    def setUp(self):
        self.tempo = git._get_revlist
        git._get_revlist = fixtures.mock_get_revlist
        self.temo2 = sys.argv
        sys.argv = [
            sys.argv[0],
            "0161cca7fec8a4b5c9ca9fccf7a393a32222da99",
            "e3b0f9c9a0945b0efa9a9295b24cf6108a6f97bb",
            "refs/head/master"
        ]

    def test_postreceive(self):
        publisher = TPublisher()
        hook = git.GitHook(publisher)
        hook.postreceive()
        self.assertEquals(publisher.payload,
                          fixtures.git_postreceive_expected_output)

    def tearDown(self):
        git._get_revlist = self.tempo
        sys.argv = self.temo2


class TestSvnHook(unittest.TestCase):

    def setUp(self):
        self.tempo = svn._svnlook
        svn._svnlook = fixtures.mock_svnlook
        self.temo2 = sys.argv
        sys.argv = [
            sys.argv[0],
            "17",
            "/var/svn/repo"
        ]

    def test_postcommit(self):
        publisher = TPublisher()
        hook = svn.SvnHook(publisher)
        hook.postcommit()
        self.assertEquals(publisher.payload,
                          fixtures.svn_postcommit_expected_output)

    def tearDown(self):
        svn._svnlook = self.tempo
        sys.argv = self.temo2

if __name__ == "__main__":
    unittest.main()
