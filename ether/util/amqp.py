#!/usr/bin/env python -tt

"""AMQP Utility functions."""

__all__ = ["BaseAMQPUtil", "AMQPUtil"]

import logging
from abc import ABCMeta

import pika

LOG = logging.getLogger(__name__)

class BaseAMQPUtil(object):

    """Base abstract class for AMQP consumers."""

    __metaclass__ = ABCMeta

    def __init__(self, config):

        """
        Initializes the base consumer object.

        :param config: Dictionary containing the needed configuration items.
        :type config: dictionary

        """

        self._host = config["host"]
        self._port = config["port"]
        self._user = config["user"]
        self._password = config["password"]
        self._vhost = config["vhost"]

        self._credentials = pika.PlainCredentials(self._user, self._password)
        self._parameters = pika.ConnectionParameters(host=self._host,
                                    port=self._port, virtual_host=self._vhost,
                                    credentials=self._credentials)

        self._connection = None
        self._channel = None

class AMQPUtil(BaseAMQPUtil):

    """Asynchronous consumer."""

    def __init__(self, config):

        """
        Setup the connection with the provided configuration.

        :param config: Dictionary containing the needed configuration items.
        :type config: dictionary
        """
        super(AMQPUtil, self).__init__(config=config)
        self.setup_connection()

    def setup_connection(self):

        """Step #1: Connect to RabbitMQ."""
        self._connection = pika.BlockingConnection(self._parameters)
        self._channel = self._connection.channel()

    def delete_queue(self, name=""):

        """Delete a queue."""
        self._channel.queue_delete(queue = name)


