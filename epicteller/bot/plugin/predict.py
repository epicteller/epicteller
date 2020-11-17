#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot import on_command, permission, CommandSession

from epicteller.core.config import Config


@on_command('p', permission=permission.PRIVATE_FRIEND)
async def predict(session: CommandSession):
    await session.send(Config.RUNTIME_ID)
