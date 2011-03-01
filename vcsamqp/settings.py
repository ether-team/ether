#!/usr/bin/python -tt

AMQP = {
    "host": "localhost",
    "port": 5672,
    "user": "vcsamqp",
    "password": "123",
    "vhost": "/vcsamqp",
    "exchange_name": "vcsamqp",
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
