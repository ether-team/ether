#!/usr/bin/env python -tt

"""AMQP sender API."""

__all__ = ["BasicAMQPPublisher", "BlockingAMQPPublisher", "AsyncAMQPPublisher"]

import logging
from abc import ABCMeta, abstractmethod

import pika
import simplejson

LOG = logging.getLogger(__name__)

class BasicAMQPPublisher(object):

    """Base abstract class for AMQP publishers."""

    __metaclass__ = ABCMeta

    def __init__(self, config):

        self._exchange = config["exchange_name"]
        self._exchange_type = config["exchange_type"]
        self._delivery_mode = config["delivery_mode"]

        self._routing_key = config["routing_key"]

        credentials = pika.PlainCredentials(config["user"],
                                            config["password"])
        self._parameters = pika.ConnectionParameters(
                                                host=config["host"],
                                                port=config["port"],
                                                virtual_host=config["vhost"],
                                                credentials=credentials)
        self._connection = None
        self._channel = None
        self._payload = None

    @abstractmethod
    def send_payload(self, payload):
        """
        Send payload to the server.
        Abstract method. Has to be implemented in derived classes.

        :param payload: data to be sent
        :type payload: dictionary

        """

        raise NotImplementedError


class BlockingAMQPPublisher(BasicAMQPPublisher):

    """
    Blocking (synchronous) publisher.
    Code is borrowed from Pika Blocking demo_send example_blocking_:

    .. _example_blocking: http://tonyg.github.com/pika/examples.html#id4

    """

    def send_payload(self, payload):
        """
        Send payload to the server using blocking approach.

        :param payload: data to be sent
        :type payload: dictionary

        """

        self._connection = pika.BlockingConnection(self._parameters)
        self._channel = self._connection.channel()

        self._channel.exchange_declare(exchange=self._exchange,
                                       type=self._exchange_type)

        properties = pika.BasicProperties("text/plain",
                                          delivery_mode=self._delivery_mode)

        self._channel.basic_publish(exchange=self._exchange,
                                    routing_key=self._routing_key,
                                    body=simplejson.dumps(payload),
                                    properties=properties)
        self._connection.close()


class AsyncAMQPPublisher(BasicAMQPPublisher):

    """

    Asynchronous Publisher.
    Code is borrowed from Pika Asynchronous demo_send example_async_:

    .. _example_async: http://tonyg.github.com/pika/examples.html#demo-send

    Methods are placed in the same order as they're called by pika

    """

    def on_connected(self, connection):
        """
        Callback. Called when we are fully connected to RabbitMQ.

        :param connection: connection object
        :type connection: object
        """
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        """
        Callback. Called when channel has opened.

        :param channel: channel object
        :type channel: object

        """
        self._channel = channel

        self._channel.basic_publish(exchange=self._exchange,
                                    routing_key=self._routing_key,
                                    body=self._payload,
                                    properties=pika.BasicProperties(
                                        content_type="text/plain",
                                        delivery_mode=self._delivery_mode))

    def send_payload(self, payload):
        """
        Send payload to the server setting up chain of callbacks:
        on_connected -> on_channel_open -> on_queue_declared.
        (see above)

        :param payload: data to be sent
        :type payload: dictionary

        """


        self._connection = pika.SelectConnection(self._parameters,
                                                 self.on_connected)
        self._payload = simplejson.dumps(payload)
        self._connection.ioloop.start()
        self._connection.close()

