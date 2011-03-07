#!/usr/bin/env python -tt

"""Configuration for svn hook."""

from ether.configs.common import host, port, user, password, \
     vhost, exchange_name

AMQP_CONFIG = {
    "host": host,
    "port": port,
    "user": user,
    "password": password,
    "vhost": vhost,
    "exchange_name": exchange_name,
    "routing_key": "",
    "exchange_type": "fanout",
    "exchange_durable": True,
    "delivery_mode": 1,
}

REPO_CONFIG = [
    ("/svn/", "https://some.site.org/svn/")
]

