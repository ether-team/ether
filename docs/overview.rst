========
Overview
========

|ether| project has one simple goal -- simplify handling of updates in version
control systems.

In a situation, where there are many version control systems (VCSes) to follow,
simple polling creates a huge load on the servers where VCSes are hosted, which
in the end results in delays between the moment when a change is available and
the moment when the change is acted upon.

Instead of polling, we decided to use a push approach: every time a change
reaches a VCS, an AMQP message is generated, which is then processed by the
actual handler.

We created a system around `RabbitMQ`_ using `pika`_ framework.

This project delivers two frameworks:

* a framework to write change handlers; see :ref:`ether`
* a framework to create and handle hooks for supported VCSes

.. _RabbitMQ: http://www.rabbitmq.com

.. _pika: http://pika.github.com/

..
    vim:ft=rst:et:ts=4:sw=4
