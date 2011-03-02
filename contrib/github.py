#!/usr/bin/python -tt

"""
This a simple shovel script to bridge github messages to the local fanout
exchnage.

The usage of multiprocessing module is to workaround a design limitation in
pika :
http://lists.rabbitmq.com/pipermail/rabbitmq-discuss/2011-February/011438.html
"""

import sys
sys.path.append(".") 
from ether.publishers.amqp import AsyncAMQPPublisher
from ether.consumers.amqp import AsyncAMQPConsumer
from ether.payload.common import Payload
from ether.settings import AMQP
from multiprocessing import Process, Queue

#import pika.log
#pika.log.setup(level=pika.log.DEBUG)


GITHUB = {
    "host": "localhost",
    "port": 5672,
    "user": "guest",
    "password": "123",
    "vhost": "/",
    "exchange_name": "github",
    "exchange_type": "topic",
    "exchange_durable": True,
    "delivery_mode": 1,
    
    "CONSUMER": {"queue_name": "github",
                 "routing_key": "github.push.#",
                 "queue_durable": True,
                 "queue_exclusive": True,
                 "queue_auto_delete": True
                 }
}

class GithubConsumer(AsyncAMQPConsumer):

    """github consumer based on Async AMQP consumer."""

    def receive_payload(self, channel, method, header, body):
        #print "putting item in q"
        PQ.put(Payload(body).payload)

def consumer():

    """ Wrapper function used by Process """

    #print "Creating consumer"
    con = GithubConsumer(config = GITHUB )
    #print "running consumer"
    con.consume()

def publisher():

    """ Wrapper function used by Process """

    pub = AsyncAMQPPublisher(AMQP)
    while True:
        #print "Blocking in publisher thread"
        try:
            pub.send_payload(PQ.get(block=True))
            #print "item sent, looping"
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == '__main__':
    try:
        PQ = Queue()
        PP = Process(target=publisher)
        PP.start()
        CP = Process(target=consumer)
        CP.start()
        PP.join()
        CP.join()
    except KeyboardInterrupt:
        sys.exit(0)

