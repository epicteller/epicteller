#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot import on_command, Bot
from nonebot.adapters.cqhttp import permission, MessageSegment, Message
from nonebot.adapters.cqhttp.event import MessageEvent

from epicteller.bot.controller.base import prepare_context
from epicteller.core import error
from epicteller.core.controller import character as character_ctl
from epicteller.core.controller import combat as combat_ctl
from epicteller.core.model.combat import Combat
from epicteller.core.model.room import Room
from epicteller.core.util.enum import CombatState, ExternalType

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
    if not combat or combat.state == CombatState.ENDED:
        await combat_cmd.finish(f'当前战斗轮指示器未激活。\n'
                                f'使用指令「{event.raw_message.strip()[0]}combat start」开启一场新战斗。')
        return
    if combat.state == CombatState.INITIATING:
        await combat_cmd.finish(f'正在决定先攻顺序。\n'
                                f'投掷先攻骰即可加入先攻顺位。')
        return
    # combat.state == CombatState.RUNNING
    token = combat.tokens[combat.order.current_token_name]
    player_name = f'「{token.name}」'
    if token.character_id:
        external_id = await character_ctl.get_character_external_id(token.character_id, ExternalType.QQ)
        if external_id:
            player_name = f'{MessageSegment.at(external_id)}'
    message = Message(f'当前正在战斗中。\n'  # TODO: 这里应该有个卡片消息实时显示战斗轮。
                      f'第 {combat.order.round_count} 回合，{player_name} 正在行动中。')
    await combat_cmd.finish(message)


async def combat_start(bot: Bot, event: MessageEvent, state: dict):
    room: Room = state['room']
    try:
        combat = await combat_ctl.start_new_combat(room)
    except error.combat.CombatRunningError:
        await combat_cmd.finish('❌ 当前战斗还在进行中。')
        return
    state['combat'] = combat


async def combat_run(bot: Bot, event: MessageEvent, state: dict):
    combat: Combat = state['combat']
    try:
        await combat_ctl.run_combat(combat)
    except error.combat.CombatEndedError:
        await combat_cmd.finish('❌ 当前并未处于战斗中，请重新开始一场战斗。')
        return
    except error.combat.CombatRunningError:
        await combat_cmd.finish('❌ 当前战斗已经进入行动阶段。')
        return
    except error.combat.CombatOrderEmptyError:
        await combat_cmd.finish('❌ 先攻列表为空，无法进入行动阶段。')
        return


async def combat_next(bot: Bot, event: MessageEvent, state: dict):
    combat: Combat = state['combat']
    try:
        await combat_ctl.next_combat_token(combat)
    except error.combat.CombatNotRunningError:
        await combat_cmd.finish('❌ 当前战斗并未处于行动阶段。')
        return
    except error.combat.CombatOrderEmptyError:
        await combat_cmd.finish('❌ 先攻列表为空，无法进入下一行动轮。')
        return


async def combat_end(bot: Bot, event: MessageEvent, state: dict):
    combat: Combat = state['combat']
    try:
        await combat_ctl.end_combat(combat)
    except error.combat.CombatEndedError:
        await combat_cmd.finish('❌ 当前战斗已结束。')
        return


# DEPRECATED
battlestart = on_command('battlestart')


@battlestart.handle()
async def _(bot: Bot, event: MessageEvent, state: dict):
    await battlestart.finish(f'「battlestart」指令已弃用。\n'
                             f'请使用指令「{event.raw_message.strip()[0]}combat」切换到新的战斗轮指示器。')



