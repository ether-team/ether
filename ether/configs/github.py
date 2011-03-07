#!/usr/bin/env python -tt

"""Configuration for github shovel script."""

from ether.configs.common import host, port, user, \
     password, vhost, exchange_name

SOURCE = {
    "host": "localhost",
    "port": 5672,
    "user": "guest",
    "password": "123",
    "vhost": "/",
    "exchange_name": "github",
    "routing_key": "github.push.#",
    "queue_name": "github",
    "queue_durable": True,
    "queue_exclusive": True,
    "queue_auto_delete": True
}

TARGET = {
    "host": host,
    "port": port,
    "user": user,
    "password": password,
    "vhost": vhost,
    "exchange_name": exchange_name,
    "routing_key": "",
    "exchange_type": "fanout",
    "exchange_durable": True,
    "delivery_mode": 1    
}

