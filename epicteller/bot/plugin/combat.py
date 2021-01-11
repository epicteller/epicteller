#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot import on_command, Bot
from nonebot.adapters.cqhttp import permission
from nonebot.adapters.cqhttp.event import MessageEvent

from epicteller.bot.controller.base import prepare_context
from epicteller.core.controller import combat as combat_ctl
from epicteller.core.model.combat import Combat
from epicteller.core.model.room import Room

combat_cmd = on_command('combat', permission=permission.GROUP)


@combat_cmd.handle()
async def _(bot: Bot, event: MessageEvent, state: dict):
    is_prepared = await prepare_context(combat_cmd, bot, event, state)
    if not is_prepared:
        await combat_cmd.finish()
        return
    room: Room = state['room']
    combat = await combat_ctl.get_room_running_combat(room)
    state['combat'] = combat
    arg = str(event.get_message()).strip()
    if arg == '':
        await combat_status(bot, event, state)
    elif arg == 'start':
        await combat_start(bot, event, state)
    elif arg == 'run':
        await combat_run(bot, event, state)
    elif arg == 'next':
        await combat_next(bot, event, state)
    elif arg == 'end':
        await combat_end(bot, event, state)


async def combat_status(bot: Bot, event: MessageEvent, state: dict):
    combat: Combat = state['combat']
    if not combat:
        await combat_cmd.finish(f'当前战斗轮指示器未激活。\n'
                                f'使用指令「{event.raw_message.strip()[0]}combat start」开启一场新战斗。')
        return
    await combat_cmd.finish(f'当前正在战斗中。\n'  # TODO: 这里应该有个卡片消息实时显示战斗轮。
                            f'')


async def combat_start(bot: Bot, event: MessageEvent, state: dict):
    pass


async def combat_run(bot: Bot, event: MessageEvent, state: dict):
    pass


async def combat_next(bot: Bot, event: MessageEvent, state: dict):
    pass


async def combat_end(bot: Bot, event: MessageEvent, state: dict):
    pass


# DEPRECATED
battlestart = on_command('battlestart')


@battlestart.handle()
async def _(bot: Bot, event: MessageEvent, state: dict):
    await battlestart.finish(f'「battlestart」指令已弃用。\n'
                             f'请使用指令「{event.raw_message.strip()[0]}combat」切换到新的战斗轮指示器。')



