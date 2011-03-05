from ether.util.amqp import AMQPUtil

util = AMQPUtil(config = GITHUB)
util.delete_queue(name = sys.argv[1])
sys.exit(0)
