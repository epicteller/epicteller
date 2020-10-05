#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import re
from os import path
from typing import Callable, List, Tuple, Pattern

import nonebot
from nonebot.command import CommandHandler_T

from epicteller.core.config import Config
from epicteller.core.kafka import Bus

_bot = None

bus = Bus(job_paths=['epicteller.bot.actor'],
          bootstrap_servers=Config.KAFKA_SERVERS)

regex_commands: List[Tuple[Pattern, str]] = []

logger = logging.getLogger('bot')


def get_bot() -> nonebot.NoneBot:
    global _bot
    if _bot:
        return _bot
    nonebot.init()
    nonebot.load_plugins(path.join(path.dirname(__file__), 'plugin'),
                         'epicteller.bot.plugin')
    _bot = nonebot.get_bot()
    _bot.server_app.config.from_object(Config)
    return _bot


def on_regex(regex: str, *, alias: str=None) -> Callable:
    def deco(func: CommandHandler_T) -> CommandHandler_T:
        pattern = re.compile(regex)
        command = alias or func.__name__
        regex_commands.append((pattern, command))
        return func
    return deco
