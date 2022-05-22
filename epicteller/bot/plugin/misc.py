#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Event
from nonebot.adapters.onebot.v11 import Bot
from nonebot.typing import T_State

from epicteller.core.config import Config
from epicteller.core.util.version import get_commit

runtime = on_command('runtime', block=True)


@runtime.handle()
async def _(bot: Bot, event: Event, state: T_State):
    hostname = Config.HOSTNAME
    commit = get_commit()
    message = (f'Hostname: {hostname}\n'
               f'Version: {commit}')
    await runtime.finish(message)
