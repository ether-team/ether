#!/usr/bin/env python -tt

"""AMQP Listener."""

__all__ = ["BaseAMQPConsumer", "AsyncAMQPConsumer"]

import logging
from abc import ABCMeta, abstractmethod

import pika, sys, simplejson
from ether.payload.common import Payload

LOG = logging.getLogger(__name__)

class BaseAMQPConsumer(object):

    """Base abstract class for AMQP consumers."""

    __metaclass__ = ABCMeta

    def __init__(self, config):

        """
        Initializes the base consumer object.

        :param config: Dictionary containing the needed configuration items.
        :type config: dictionary

        """

        self._exchange = config["exchange_name"]

        self._routing_key = config["routing_key"]
        self._queue = config["queue_name"]
        self._durable = config["queue_durable"]
        self._exclusive = config["queue_exclusive"]
        self._auto_delete = config["queue_auto_delete"]


        credentials = pika.PlainCredentials(config["user"],
                                            config["password"])
        self._parameters = pika.ConnectionParameters(
            host=config["host"], port=config["port"],
            virtual_host=config["vhost"], credentials=credentials)

        self._connection = None
        self._channel = None
        self._payload = None

    def receive_payload(self, channel, method, header, body):

        """
        Recieve payload from the server.
        Abstract method. Has to be implemented in derived classes.

        :param body: data received
        :type body: dictionary
        """

        payload = Payload(body)
        self._payload = payload

        return self.process_payload(payload, method.routing_key)

    @abstractmethod
    def process_payload(self, payload, routing_key=None):

        """
        Process payload.
        Abstract method. Has to be implemented in derived classes.

        :param payload: received payload
        :type body: dictionary

        :param routing_key: AMQP routing key
        :type routing_key: string

        :returns: result code
        :rtype: int
        """

        raise NotImplementedError



class AsyncAMQPConsumer(BaseAMQPConsumer):

    """Asynchronous consumer."""

    def __init__(self, config=AMQP):

        """
        Setup the connection with the provided configuration.

        :param config: Dictionary containing the needed configuration items.
        :type config: dictionary
        """

        BaseAMQPConsumer.__init__(self, config = config)
        self.setup_connection()

    def setup_connection(self):

        """Step #1: Connect to RabbitMQ."""

        self._connection = pika.adapters.SelectConnection(self._parameters,
                                                          self.on_connected)

    def on_connected(self, connection):

        """
        Step #2: Called when we are fully connected to RabbitMQ.

        :param connection: connection object
        :type connection: object
        """

        self._connection = connection
        self._connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):

        """
        Step #3: Called when our channel has opened.

        :param channel: channel object
        :type channel: object
        """

        self._channel = channel
        channel.queue_declare(queue = self._queue,
                              durable = self._durable,
                              exclusive = self._exclusive,
                              auto_delete = self._auto_delete,
                              callback = self.on_queue_declared)

    # Step #4
    def on_queue_declared(self, frame):

        """
        Step #5: Called when Queue has been declared.

        frame is the response from RabbitMQ
        """

        self._channel.queue_bind(queue = self._queue,
                                exchange = self._exchange,
                                routing_key = self._routing_key,
                                callback = self.on_queue_bound)

    def on_queue_bound(self, frame):

        """
        Step #6: Called when the queue has been bound to the exchange.

        :param _frame: response from broker
        :type _frame: object
        """

        self._channel.basic_consume(self.receive_payload,
                                   queue = self._queue,
                                   no_ack = True)

    def consume(self):

        """Start the IO event loop so we can communicate with RabbitMQ."""

        try:
            self._connection.ioloop.start()
        except KeyboardInterrupt:
            # Gracefully close the connection
            self._connection.close()
            # Loop until we're fully closed, will stop on its own
            self._connection.ioloop.start()


class TestConsumer(AsyncAMQPConsumer):

    def process_payload(self, payload, routing_key):
        print "%s: %s" % (routing_key, payload.payload)

def main(argv):
    consumer = TestConsumer(config = AMQP)
    consumer.consume()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
