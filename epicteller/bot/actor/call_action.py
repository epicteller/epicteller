#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from epicteller.bot import get_bot, bus

bot = get_bot()


@bus.on('call_action')
async def call_action(topic: str, data: str) -> None:
    try:
        data = json.loads(data)
    except ValueError:
        return
    if 'params' not in data or 'params' not in data:
        return
    self_id = str(data['params'].get('self_id'))
    if self_id and self_id not in bot._wsr_api_clients:
        return
    await bot.call_action(data['action'], **data['params'])
