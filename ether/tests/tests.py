import os
import sys

import pika

from ether.tests import fixtures, dummy, runner
from ether.hooks import git, svn
from ether import consumer, publisher
from ether.util import amqp as util
from ether.configs.svn_postcommit import AMQP_CONFIG, REPO_CONFIG
from ether.configs.test_consumer import TEST_CONFIG


class TPublisher(object):

    def __init__(self):
        self.payload = None

    def send_payload(self, payload):
        self.payload = payload


class TConsumer(consumer.AsyncAMQPConsumer):

    def process_payload(self, payload, routing_key=None):
        self.payload = payload
        self.routing_key = routing_key


class TestGitHook(runner.DummyTestCase):

    def test_postreceive(self):
        self.mock(git, "_get_allbranches", dummy.dummy_get_allbranches)
        self.mock(git, "_get_notcommits", dummy.dummy_get_notcommits)
        self.mock(git, "_get_ataginfo", dummy.dummy_get_ataginfo)
        self.mock(git, "_get_revlistinfo", dummy.dummy_get_revlistinfo)
        self.mock(git, "_get_revtype", lambda rev: "tag")
        publisher = TPublisher()
        hook = git.GitHook(publisher)
        hook.postreceive(dummy.generate_git_commits())
        self.assertEquals(publisher.payload,
                          fixtures.githook_payload)
        # Test behavior (not state) multiple cases
        self.mock(git, "_get_types", lambda old, new, ref: ("create",
                                                            "unannotated tag"))
        hook.postreceive(dummy.generate_git_commits())

        self.mock(git, "_get_types", lambda old, new, ref: ("create",
                                                            "annotated tag"))
        hook.postreceive(dummy.generate_git_commits())
        self.mock(git, "_get_types", lambda old, new, ref: ("delete",
                                                            "annotated tag"))
        hook.postreceive(dummy.generate_git_commits())

        self.mock(git, "_get_types", lambda old, new, ref: ("delete",
                                                            "branch"))
        hook.postreceive(dummy.generate_git_commits())
        self.mock(git, "_get_types", lambda old, new, ref: ("update",
                                                            "branch"))
        hook.postreceive(dummy.generate_git_commits())
        self.mock(git, "_get_types", lambda old, new, ref: ("create",
                                                            "branch"))
        hook.postreceive(dummy.generate_git_commits())

    def test_get_types(self):
        # Case 1
        self.mock(git, "_get_revtype", lambda rev: "tag")
        change_type, ref_type = git._get_types(
            "0000", "0000", "refs/tags/TAG_NAME")
        self.assertEquals(change_type, "create")
        self.assertEquals(ref_type, "annotated tag")
        # Case 2
        self.mock(git, "_get_revtype", lambda rev: "commit")
        change_type, ref_type = git._get_types(
            "1111", "0000", "refs/tags/TAG_NAME")
        self.assertEquals(change_type, "delete")
        self.assertEquals(ref_type, "unannotated tag")
        # Case 3
        change_type, ref_type = git._get_types(
            "1111", "1111", "refs/heads/master")
        self.assertEquals(change_type, "update")
        self.assertEquals(ref_type, "branch")
        # Case 4
        change_type, ref_type = git._get_types(
            "XXXX", "XXXX", "bugaga")
        self.assertEquals(ref_type, "unknown")

    def test_wrappers(self):
        """Make sure that the wrappers are OK."""
        self.unmock()
        git._get_allbranches()
        git._get_notcommits("branch1")
        git._get_ataginfo("ref")
        git._get_revlistinfo("rev")
        git._get_revtype("rev")


class TestSvnHook(runner.DummyTestCase):

    def setUp(self):
        self.mock(svn, "_svnlook", dummy.dummy_svnlook)

    def test_postcommit(self):
        publisher = TPublisher()
        hook = svn.SvnHook(publisher, REPO_CONFIG)
        hook.postcommit(
            "17",
            "/var/svn/repo")
        self.assertEquals(publisher.payload,
                          fixtures.svnhook_payload)

    def test_wrappers(self):
        """Make sure that the wrappers are OK."""
        self.unmock()
        svn._svnlook('log', 'bla', 1, '/bin/true')

    def test_get_repo_url(self):
        self.assertRaises(svn.SvnHookError, svn.get_repo_url, [], None)
        self.assertRaises(svn.SvnHookError, svn.get_repo_url,
                          ["whatever", "/some/path"],
                          (("/some/path", "url1"), ("", "url2")))

class TestPublisher(runner.DummyTestCase):

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
        tpublisher = publisher.AsyncAMQPPublisher(AMQP_CONFIG)
        tpublisher.send_payload({"payload":"payload"})
        # Test callbacks
        tpublisher.on_connected(dummy.DummySelectConnection(None, None))
        tpublisher.on_channel_open(dummy.DummyChannel())


class TestConsumer(runner.DummyTestCase):

    def setUp(self):
        self.mock(consumer.pika, "PlainCredentials",
                dummy.DummyPlainCridentials)
        self.mock(consumer.pika, "ConnectionParameters",
                dummy.DummyConnectionParameters)
        self.mock(consumer.pika, "BlockingConnection",
                dummy.DummyBlockingConnection)
        self.mock(consumer.pika, "BasicProperties",
                dummy.DummyBasicProperties)
        self.mock(consumer.pika.adapters, "SelectConnection",
                dummy.DummySelectConnection)

    def test_ansync_methods(self):
        tconsumer = TConsumer(TEST_CONFIG)
        tconsumer.consume()
        # Test callbacks
        tconsumer.setup_connection()
        tconsumer.on_connected(dummy.DummySelectConnection(None, None))
        tconsumer.on_channel_open(dummy.DummyChannel())
        tconsumer.on_queue_declared("some_frame")
        tconsumer.on_queue_bound("some_frame")

    def test_receive_payload(self):
        tconsumer = TConsumer(TEST_CONFIG)
        tconsumer.receive_payload(None, dummy.DummyMethod(),
                                 None, '{"payload":{"data":"data"}}')

    def test_abstract_method(self):
        tconsumer = TConsumer(TEST_CONFIG)
        self.assertRaises(NotImplementedError,
                          consumer.AsyncAMQPConsumer.process_payload,
                          tconsumer, None, None)

    def test_receive_payload_exception(self):
        self.assertRaises(TypeError, consumer.AsyncAMQPConsumer, TEST_CONFIG)

    def test_exceptional_consume(self):
        consumer.pika.adapters.SelectConnection = \
                dummy.DummyExceptionalSelectConnection
        tconsumer = TConsumer(TEST_CONFIG)
        tconsumer.consume()


class TestUtils(runner.DummyTestCase):

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
        obj = util.AMQPUtil(TEST_CONFIG)
        obj.setup_connection()
        obj.delete_queue()
