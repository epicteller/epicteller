#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot import on_command
from nonebot.adapters.cqhttp import Event
from nonebot.adapters.cqhttp import Bot

from epicteller.core.util.version import get_commit

version = on_command('version')


@version.handle()
async def _(bot: Bot, event: Event, state: dict):
    commit = get_commit()
    await version.finish(commit)
