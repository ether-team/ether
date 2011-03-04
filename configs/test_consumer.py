#!/usr/bin/env python -tt

"""Configuration for test consumer."""

from ether.configs.common import host, port, user, \
     password, vhost, exchange_name

TEST_CONFIG = {
    "host": host,
    "port": port,
    "user": user,
    "password": password,
    "vhost": vhost,
    "exchange_name": exchange_name,
    "routing_key": "",
    "queue_name": "",
    "routing_key": "",
    "queue_durable": True,
    "queue_exclusive": True,
    "queue_auto_delete": True
}
