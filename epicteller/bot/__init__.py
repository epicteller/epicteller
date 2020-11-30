#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import logging
import re
import threading
from typing import Callable, List, Tuple, Pattern

from nonebot.typing import Handler

from epicteller.core.config import Config
from epicteller.core.kafka import Bus

bus = Bus(job_paths=['epicteller.bot.actor'],
          bootstrap_servers=Config.KAFKA_SERVERS)


def start_bus():
    def _thread():
        bus.loop = asyncio.new_event_loop()
        bus.loop.run_until_complete(bus.run())
    thread = threading.Thread(target=_thread)
    thread.start()
