#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot import on_command, permission, Bot
from nonebot.typing import Event

from epicteller.core.config import Config
from epicteller.core.controller import dice as dice_ctl

predict = on_command('p', permission=permission.PRIVATE_FRIEND)


@predict.handle()
async def _(bot: Bot, event: Event, state: dict):

    try:
        await dice_ctl.update_memory_dump()
        print(Config.RUNTIME_ID)
    except Exception as e:
        print(e)
        raise
    await predict.finish(str(Config.RUNTIME_ID))
