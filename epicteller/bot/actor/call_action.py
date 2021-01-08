#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import traceback

import nonebot

from epicteller.bot import bus


@bus.on('call_action')
async def call_action(topic: str, data: str) -> None:
    data = json.loads(data)
    if 'params' not in data or 'self_id' not in data['params']:
        return
    self_id = str(data['params']['self_id'])
    bots = nonebot.get_bots()
    if self_id and self_id not in bots:
        return
    data['params'].pop('self_id')
    bot = bots[self_id]
    await bot.call_api(data['action'], **data['params'])
