#!/usr/bin/env python -tt

"""Testcases for Ether APIs."""

# pylint: disable=C0111

import unittest
import imp

from collections import defaultdict

import dummy

import ether
from ether.hooks import git, svn, get_repo_url, EtherHookError
from ether import consumer, publisher
from ether.util import amqp as util

SVN_PCOMMIT = imp.load_source("svn_postcommit_config",
                              "configs/svn_postcommit.conf")

GIT_PRECEIVE = imp.load_source("git_postreceive_config",
                               "configs/git_postreceive.conf")

CONS_CONF = imp.load_source("test_consumer_config",
                            "configs/test_consumer.conf")

class DummyTestCase(unittest.TestCase):
    """A test case that provides an easy way to mock the modules."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(DummyTestCase, self).__init__(*args, **kwargs)
        self._originals = defaultdict(dict)

    def mock(self, module_imported, original, stub):
        """Mocks the module.

        :param module_imported: module where the substitution has to occur
        :param original: string name of the module to substitute
        :param stub: a module that is supposed to take place of the original
        """
        if original not in self._originals[module_imported]:
            self._originals[module_imported][original] = \
                    getattr(module_imported, original)
        setattr(module_imported, original, stub)

    def unmock(self):
        """Unmocks the modules. Sets everything to initial condition."""
        for module_imported, originals in self._originals.iteritems():
            for original_name, module in originals.iteritems():
                setattr(module_imported, original_name, module)

        self._originals.clear()

    def tearDown(self): #C0103:
        """Unmocks the modules."""
        self.unmock()


class TPublisher(object):

    def __init__(self):
        self.payload = None

    def send_payload(self, payload):
        self.payload = payload


class TConsumer(consumer.AsyncAMQPConsumer):

    def process_payload(self, payload, routing_key=None):
        self.payload = payload
        self.routing_key = routing_key

class TestGeneralHook(unittest.TestCase):

    def test_get_repo_url(self):
        self.assertRaises(EtherHookError, get_repo_url, [], None)
        self.assertRaises(EtherHookError, get_repo_url,
                          ["whatever", "/some/path"],
                          (("/some/path", "url1"), ("", "url2")))

class TestGitHook(DummyTestCase):

    @staticmethod
    def _generate_git_commits():
        return [[
            "aa453216d1b3e49e7f6f98441fa56946ddcd6a20",
            "68f7abf4e6f922807889f52bc043ecd31b79f814",
            "refs/heads/master"]]

    @staticmethod
    def _githook_payload():
        return {
            'commits': [],
            'after': '68f7abf4e6f922807889f52bc043ecd31b79f814',
            'ref': 'refs/heads/master',
            'repository': {
                'url': 'ssh://git@some.site.org/git/',
                'owner': {
                    'email': '',
                    'name': ''},
                'name': '',
                'description': ''},
            'before': 'aa453216d1b3e49e7f6f98441fa56946ddcd6a20'
        }

    @staticmethod
    def _dummy_get_allbranches():
        """
        git for-each-ref --format='%(refname)' refs/heads/
        """
        return """\
refs/heads/master
refs/heads/test
"""

    @staticmethod
    def _dummy_get_notcommits(other_branches):
        """
        git rev-parse --not BRANCH1 BRANCH2 ... BRANCHN
        """
        return "^0db3f7da89cfb8ef301c1f4a5cb1d8cfcad13684"

    @staticmethod
    def _dummy_get_ataginfo(ref_):
        """
        git for-each-ref
        --format='%(*authorname)|%(*authoremail)|%(*authordate)|%(*subject)'
        refs/tags/TAG_NAME
        """
        return """\
Some One|<some.one@example.com>|Sat Feb 19 14:27:55 2011 +0200|changelog updated
"""

    @staticmethod
    def _dummy_get_revlistinfo(rev_):
        """
        git rev-list --pretty=format:'%an|%ae|%ad|%s%n' refs/???
        """
        return """\
commit 9442f7cdd33e93e7cf0add43bd9bc4be1bfbdb72
Some One|<some.one@example.com>|Thu Mar 3 16:21:11 2011 +0200|Commit 1

commit ee43557cdc68039e13bdddb3dd270028334eb5a1
Some One|<some.one@example.com>|Thu Mar 3 14:21:46 2011 +0200|Commit 2"""

    def test_postreceive(self):
        self.mock(git, "_get_allbranches", self._dummy_get_allbranches)
        self.mock(git, "_get_notcommits", self._dummy_get_notcommits)
        self.mock(git, "_get_ataginfo", self._dummy_get_ataginfo)
        self.mock(git, "_get_revlistinfo", self._dummy_get_revlistinfo)
        self.mock(git, "_get_revtype", lambda rev: "tag")

        publisher = TPublisher()
        hook = git.GitHook(publisher, GIT_PRECEIVE.REPO_CONFIG)
        hook.postreceive(self._generate_git_commits())
        self.assertEquals(publisher.payload, self._githook_payload())

        # Test behavior (not state) multiple cases
        self.mock(git, "_get_types", lambda old, new, ref: ("create",
                                                            "unannotated tag"))
        hook.postreceive(self._generate_git_commits())

        self.mock(git, "_get_types", lambda old, new, ref: ("create",
                                                            "annotated tag"))
        hook.postreceive(self._generate_git_commits())
        self.mock(git, "_get_types", lambda old, new, ref: ("delete",
                                                            "annotated tag"))
        hook.postreceive(self._generate_git_commits())

        self.mock(git, "_get_types", lambda old, new, ref: ("delete",
                                                            "branch"))
        hook.postreceive(self._generate_git_commits())
        self.mock(git, "_get_types", lambda old, new, ref: ("update",
                                                            "branch"))
        hook.postreceive(self._generate_git_commits())
        self.mock(git, "_get_types", lambda old, new, ref: ("create",
                                                            "branch"))
        hook.postreceive(self._generate_git_commits())

    def test_get_types_1(self):
        self.mock(git, "_get_revtype", lambda rev: "tag")
        change_type, ref_type = git._get_types("0000", "0000",
                                               "refs/tags/TAG_NAME")
        self.assertEquals(change_type, "create")
        self.assertEquals(ref_type, "annotated tag")

    def test_get_types_2(self):
        self.mock(git, "_get_revtype", lambda rev: "commit")
        change_type, ref_type = git._get_types("1111", "0000",
                                               "refs/tags/TAG_NAME")
        self.assertEquals(change_type, "delete")
        self.assertEquals(ref_type, "unannotated tag")

    def test_get_types_3(self):
        self.mock(git, "_get_revtype", lambda rev: "commit")
        change_type, ref_type = git._get_types("1111", "1111",
                                               "refs/heads/master")
        self.assertEquals(change_type, "update")
        self.assertEquals(ref_type, "branch")

    def test_get_types_4(self):
        self.mock(git, "_get_revtype", lambda rev: "commit")
        change_type, ref_type = git._get_types("xxxx", "xxxx", "bugaga")
        self.assertEquals(ref_type, "unknown")

    def test_wrappers(self):
        self.unmock()
        git._get_allbranches()
        git._get_notcommits("branch1")
        git._get_ataginfo("ref")
        git._get_revlistinfo("rev")
        git._get_revtype("rev")


class TestSvnHook(DummyTestCase):

    @staticmethod
    def _dummy_svnlook(what, repos_, rev_):
        data = {
            "changed": "U   test\n",
            "log": "commit 20\n",
            "author": "ed\n",
            "date": "2011-02-10 11:33:32 +0200 (Thu, 10 Feb 2011)\n"
        }
        return [data[what]]

    @staticmethod
    def _get_svnhook_payload():
        return {
            'data': {},
            'payload': {
                'commits': [
                    {'added': [],
                    'author': {
                        'name': ['ed\n'],
                        'email': ''},
                    'timestamp': [
                        '2011-02-10 11:33:32 +0200 (Thu, 10 Feb 2011)\n'
                    ],
                    'modified': ['test'],
                    'message': ['commit 20\n'],
                    'removed': [],
                    'id': '/var/svn/repo'}
                ],
                'repository': {
                    'url': 'https://some.site.org/svn/',
                    'owner': '',
                    'name': ''
                }
            }
        }

    def setUp(self):
        self.mock(svn, "_svnlook", self._dummy_svnlook)

    def test_postcommit(self):
        publisher = TPublisher()
        hook = svn.SvnHook(publisher, SVN_PCOMMIT.REPO_CONFIG)
        hook.postcommit(
            "17",
            "/var/svn/repo")
        self.assertEquals(publisher.payload,
                          self._get_svnhook_payload())

    def test_wrappers(self):
        self.unmock()
        svn._svnlook('log', 'bla', 1, '/bin/true')

class TestPublisher(DummyTestCase):

    def setUp(self):
        self.mock(publisher.pika, "PlainCredentials",
                  dummy.DummyPlainCridentials)
        self.mock(publisher.pika, "ConnectionParameters",
                  dummy.DummyConnectionParameters)
        self.mock(publisher.pika, "BlockingConnection",
                  dummy.DummyBlockingConnection)
        self.mock(publisher.pika, "BasicProperties",
                  dummy.DummyBasicProperties)
        self.mock(publisher.pika, "SelectConnection",
                  dummy.DummySelectConnection)

    def test_send_async_payload(self):
        tpublisher = publisher.AsyncAMQPPublisher(SVN_PCOMMIT.AMQP_CONFIG)
        tpublisher.send_payload({"payload":"payload"})
        # Test callbacks
        tpublisher.on_connected(dummy.DummySelectConnection(None, None))
        tpublisher.on_channel_open(dummy.DummyChannel())

    def test_version(self):
        reload(ether)
        self.assertTrue(hasattr(ether, "VERSION"))
        self.assertTrue(hasattr(ether, "VERSION_STR"))

class TestConsumer(DummyTestCase):

    def setUp(self):
        self.mock(consumer.pika, "PlainCredentials",
                dummy.DummyPlainCridentials)
        self.mock(consumer.pika, "ConnectionParameters",
                dummy.DummyConnectionParameters)
        self.mock(consumer.pika, "BlockingConnection",
                dummy.DummyBlockingConnection)
        self.mock(consumer.pika, "BasicProperties",
                dummy.DummyBasicProperties)
        self.mock(consumer.pika, "SelectConnection",
                dummy.DummySelectConnection)

    def test_ansync_methods(self):
        tconsumer = TConsumer(CONS_CONF.TEST_CONFIG)
        tconsumer.consume()
        # Test callbacks
        tconsumer.setup_connection()
        tconsumer.on_connected(dummy.DummySelectConnection(None, None))
        tconsumer.on_channel_open(dummy.DummyChannel())
        tconsumer.on_queue_declared("some_frame")
        tconsumer.on_queue_bound("some_frame")

    def test_receive_payload(self):
        tconsumer = TConsumer(CONS_CONF.TEST_CONFIG)
        tconsumer.receive_payload(None, dummy.DummyMethod(),
                                 None, '{"payload":{"data":"data"}}')

    def test_abstract_method(self):
        tconsumer = TConsumer(CONS_CONF.TEST_CONFIG)
        self.assertRaises(NotImplementedError,
                          consumer.AsyncAMQPConsumer.process_payload,
                          tconsumer, None, None)

    def test_receive_payload_exception(self):
        self.assertRaises(TypeError, consumer.AsyncAMQPConsumer,
                          CONS_CONF.TEST_CONFIG)

    def test_exceptional_consume(self):
        consumer.pika.SelectConnection = \
                dummy.DummyExceptionalSelectConnection
        tconsumer = TConsumer(CONS_CONF.TEST_CONFIG)
        tconsumer.consume()


class TestUtils(DummyTestCase):

    def setUp(self):
        self.mock(consumer.pika, "PlainCredentials",
                dummy.DummyPlainCridentials)
        self.mock(consumer.pika, "ConnectionParameters",
                dummy.DummyConnectionParameters)
        self.mock(consumer.pika, "BlockingConnection",
                dummy.DummyBlockingConnection)
        self.mock(consumer.pika, "BasicProperties",
                dummy.DummyBasicProperties)

    def test_amqp_util(self):
        obj = util.AMQPUtil(CONS_CONF.TEST_CONFIG)
        obj.setup_connection()
        obj.delete_queue()
