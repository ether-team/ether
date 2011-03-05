from ether.util.amqp import AMQPUtil
from ether.configs.basic import CONFIG

util = AMQPUtil(CONFIG)
util.delete_queue(name = sys.argv[1])
sys.exit(0)
