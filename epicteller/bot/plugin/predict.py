#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot import on_command, permission, CommandSession

from epicteller.core.config import Config
from epicteller.core.controller import dice as dice_ctl


@on_command('p', permission=permission.PRIVATE_FRIEND)
async def predict(session: CommandSession):
    await dice_ctl.update_memory_dump()
    await session.send(Config.RUNTIME_ID)
