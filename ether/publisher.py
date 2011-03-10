#!/usr/bin/env python -tt

"""AMQP Publisher API."""

__all__ = ["AsyncAMQPPublisher"]

import logging

import pika
import simplejson

LOG = logging.getLogger(__name__)


class AsyncAMQPPublisher(object):

    """
    Base class for AMQP publishers.

    Code is borrowed from Pika Asynchronous demo_send example_async_:

    .. _example_async: http://tonyg.github.com/pika/examples.html#demo-send

    Methods are placed in the same order as they're called by pika

    """

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
        self._connection.close()

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
