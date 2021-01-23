#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot import on_command
from nonebot.adapters.cqhttp import Event
from nonebot.adapters.cqhttp import Bot

from epicteller.core.config import Config
from epicteller.core.util.version import get_commit

runtime = on_command('runtime')


@runtime.handle()
async def _(bot: Bot, event: Event, state: dict):
    hostname = Config.HOSTNAME
    commit = get_commit()
    message = (f'Hostname: {hostname}\n'
               f'Version: {commit}')
    await runtime.finish(message)
