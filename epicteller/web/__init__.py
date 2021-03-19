#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio

from epicteller.core.config import Config
from epicteller.core.kafka import Bus

bus = Bus(bootstrap_servers=Config.KAFKA_SERVERS)


def bus_init():
    asyncio.create_task(bus.run())
