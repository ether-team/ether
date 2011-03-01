#!/usr/bin/python -tt

AMQP = {
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
