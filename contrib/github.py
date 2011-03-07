#!/usr/bin/python -tt

"""
This a simple shovel script to bridge github messages to the local fanout
exchange.

multiprocessing module is used to workaround a design limitation in pika:

  http://lists.rabbitmq.com/pipermail/rabbitmq-discuss/2011-February/011438.html
"""

import sys
sys.path.append(".")
from ether.publishers.amqp import AsyncAMQPPublisher
from ether.consumers.amqp import AsyncAMQPConsumer
from ether.configs.github import SOURCE, TARGET
from multiprocessing import Process, Queue
try:
    from setproctitle import setproctitle
except ImportError:
    print "setproctitle module not found"
    def setproctitle(name):
        """dummy function"""
        print name
        return

#import pika.log
#pika.log.setup(level=pika.log.DEBUG)


class GithubConsumer(AsyncAMQPConsumer):
    """github consumer based on Async AMQP consumer."""

    def __init__(self, config, queue):
        super(GithubConsumer, self).__init__(self, config)

        self._queue = queue

    def process_payload(self, payload, routing_key=None):
        #print "putting item in q"
        print payload
        self._queue.put(payload.payload)

def consumer(queue):
    """ Wrapper function used by Process """

    setproctitle("github-consumer")

    #print "Creating consumer"
    con = GithubConsumer(SOURCE, queue)
    #print "running consumer"
    con.consume()

def publisher(queue):
    """ Wrapper function used by Process """

    setproctitle("amqp-publisher")

    pub = AsyncAMQPPublisher(TARGET)
    while True:
        #print "Blocking in publisher thread"
        try:
            payload = queue.get(block=True)
            pub.send_payload(payload)
            #print "item sent, looping"
        except KeyboardInterrupt:
            sys.exit(0)

def main():
    """
    CLI entry point
    """

    setproctitle("github launcher")

    try:
        queue = Queue()
        pprocess = Process(target=publisher, args=(queue,))
        pprocess.start()
        cprocess = Process(target=consumer, args=(queue,))
        cprocess.start()
        pprocess.join()
        cprocess.join()
    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    sys.exit(main())
