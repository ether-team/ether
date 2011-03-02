#!/usr/bin/python -tt
from ether.publishers.amqp import AsyncAMQPPublisher
from ether.consumers.amqp import AsyncAMQPConsumer
from ether.payload.common import Payload

"""
This a simple shovel script to bridge github messages to the local fanout
exchnage.
"""

GITHUB = {
    "host": "localhost",
    "port": 5672,
    "user": "ether",
    "password": "123",
    "vhost": "/ether",
    "exchange_name": "ether",
    "exchange_type": "fanout",
    "exchange_durable": True,
    "delivery_mode": 1,
    
    "PUBLISHER": {"queue_name": "",
                  "routing_key": "",
                  "queue_durable": True,
                  "queue_exclusive": False,
                  "queue_auto_delete": False
                  },

    "CONSUMER": {"queue_name": "",
                 "routing_key": "",
                 "queue_durable": True,
                 "queue_exclusive": True,
                 "queue_auto_delete": True
                 }
}

class githubConsumer(AsyncAMQPConsumer):

    """github consumer based on Async AMQP consumer."""
    def __init__(self, config=None)
        super(self, AsyncAMQPConsumer).__init__(config = config)
        self.publisher = AsyncAMQPPublisher()

    def receive_payload(self, channel, method, header, body):
        self._payload = Payload(body)
        print self._payload
        self.publisher.send_payload(self._payload)
        

consumer = githubConsumer(config = GITHUB )
cosumer.consume()



