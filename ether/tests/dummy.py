import fixtures


#ether.hooks.svn._svnlook
def dummy_svnlook(what, repos, rev):
    data = {
        "changed": "U   test\n",
        "log": "commit 20\n",
        "author": "ed\n",
        "date": "2011-02-10 11:33:32 +0200 (Thu, 10 Feb 2011)\n"}
    return [data[what]]


#ether.hooks.git._get_allbranches
def dummy_get_allbranches():
    """
    git for-each-ref --format='%(refname)' refs/heads/
    """
    return fixtures.all_branchs


#ether.hooks.git._get_notcommits
def dummy_get_notcommits(other_branches):
    """
    git rev-parse --not BRANCH1 BRANCH2 ... BRANCHN
    """
    return fixtures.not_commits


#ether.hooks.git._get_ataginfo
def dummy_get_ataginfo(ref):
    """
    git for-each-ref
    --format='%(*authorname)|%(*authoremail)|%(*authordate)|%(*subject)'
    refs/tags/TAG_NAME
    """
    return fixtures.ataginfo


#ether.hooks.git._get_revlistinfo
def dummy_get_revlistinfo(rev):
    """
    git rev-list --pretty=format:'%an|%ae|%ad|%s%n' refs/???
    """
    return fixtures.revlistinfo


def generate_git_commits():
    return [[
        "aa453216d1b3e49e7f6f98441fa56946ddcd6a20",
        "68f7abf4e6f922807889f52bc043ecd31b79f814",
        "refs/heads/master"]]


#pika.PlainCredentials
class DummyPlainCridentials:

    def __init__(self, username, password):
        pass


#pika.ConnectionParameters
class DummyConnectionParameters:

    def __init__(self,
                 host='localhost',
                 port=666,
                 virtual_host='/',
                 credentials=None,
                 channel_max=0,
                 frame_max=13,
                 heartbeat=0):
        pass


#pika's channel
class DummyChannel:

    def exchange_declare(self, exchange, type):
        pass

    def queue_declare(self, queue, durable, exclusive, auto_delete,
                      callback=None):
        pass

    def queue_delete(self, queue):
        pass

    def basic_publish(self, exchange, routing_key, body, properties):
        pass

    def queue_bind(self, queue, exchange, routing_key, callback):
        pass

    def basic_consume(self, consumer_callback, queue="", no_ack=False,
                      exclusive=False, consumer_tag=None):
        pass



#pika.BlockingConnection
class DummyBlockingConnection:

    def __init__(self, parameters):
        pass

    def channel(self, callback=None):
        return DummyChannel()

    def close(self):
        pass


#pika.BasicProperties
class DummyBasicProperties:

    def __init__(self, content_type, delivery_mode):
        pass


#pika's ioloop
class DummyIOLoop:

    def start(self):
        pass

#pika's ioloop
class DummyExceptionalIOLoop(DummyIOLoop):
    started = False

    def start(self):
        if not self.__class__.started:
            self.__class__.started = True
            raise KeyboardInterrupt()


#pika.SelectConnection
class DummySelectConnection(DummyBlockingConnection):

    def __init__(self, parameters, on_connected):
        self.ioloop = DummyIOLoop()

    def close(self):
        pass


#pika.SelectConnection
class DummyExceptionalSelectConnection(DummySelectConnection):

    def __init__(self, parameters, on_connected):
        self.ioloop = DummyExceptionalIOLoop()


#ether.consumer.amqp.BaseAMQPConsumer.receive_payload
class DummyMethod:
    routing_key = "the_key"



