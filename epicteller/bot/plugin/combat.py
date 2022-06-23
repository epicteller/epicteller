#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
from typing import Type, Optional

from nonebot import on_command, Bot, on_message
from nonebot.adapters.onebot.v11 import permission, Message, MessageSegment
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.matcher import Matcher
from nonebot.rule import regex
from nonebot.typing import T_State

from epicteller.bot.controller import combat as combat_bot_ctl
from epicteller.bot.controller.base import prepare_context
from epicteller.core import error
from epicteller.core.controller import combat as combat_ctl
from epicteller.core.model.character import Character
from epicteller.core.model.combat import Combat
from epicteller.core.model.room import Room
from epicteller.core.util.enum import CombatState

combat_cmd = on_command('combat', permission=permission.GROUP, block=True)


@combat_cmd.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, args: Message = CommandArg()):
    await prepare_combat_context(combat_cmd, bot, event, state)
    arg = args.extract_plain_text()
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


async def combat_status(bot: Bot, event: MessageEvent, state: T_State):
    combat: Combat = state['combat']
    if not combat or combat.state == CombatState.ENDED:
        await combat_cmd.finish(f'战斗轮指示器未激活。\n'
                                f'- 使用指令「{event.raw_message.strip()[0]}combat start」开启一场新战斗。')
        return
    # await combat_cmd.send(Message(MessageSegment.xml(await combat_bot_ctl.format_combat_xml(combat))))
    await combat_cmd.send(MessageSegment.share(f'https://www.epicteller.com/combat/{combat.url_token}'))
    if combat.state == CombatState.INITIATING:
        if len(combat.order.order_list) == 0:
            status_msg = '还没有人进入先攻顺位。'
        else:
            status_msg = f'已有 {len(combat.order.order_list)} 人进入先攻顺位。'
        await combat_cmd.finish(f'当前战斗正处于先攻阶段，投掷先攻骰来决定先攻顺序。\n{status_msg}\n'
                                f'- 使用指令「{event.raw_message.strip()[0]}combat run」进入行动阶段。')
        return
    # combat.state == CombatState.RUNNING
    token = combat.tokens[combat.order.current_token_name]
    player_name = await combat_bot_ctl.format_token_message(token)
    message = Message(f'当前正在战斗中。\n'  # TODO: 这里应该有个卡片消息实时显示战斗轮。
                      f'第 {combat.order.round_count} 回合，{player_name} 正在行动中。\n'
                      f'- 使用指令「{event.raw_message.strip()[0]}combat end」结束战斗。')
    await combat_cmd.finish(message)


async def combat_start(bot: Bot, event: MessageEvent, state: T_State):
    room: Room = state['room']
    try:
        combat = await combat_ctl.start_new_combat(room)
    except error.combat.CombatRunningError:
        await combat_cmd.finish('❌ 当前战斗还在进行中。')
        return
    await combat_cmd.send(MessageSegment.share(f'https://www.epicteller.com/combat/{combat.url_token}'))
    await combat_cmd.finish(f'进入先攻阶段，战斗轮指示器已激活。\n'
                            f'投掷先攻骰来决定先攻顺序。\n'
                            f'- 在战斗的任意时刻，使用指令「{event.raw_message.strip()[0]}combat」检查战斗状态。\n'
                            f'- 使用指令「{event.raw_message.strip()[0]}combat run」进入行动阶段。')


async def combat_run(bot: Bot, event: MessageEvent, state: T_State):
    combat: Combat = state['combat']
    try:
        await combat_ctl.run_combat(combat)
    except error.combat.CombatEndedError:
        await combat_cmd.finish('❌ 当前并未处于战斗中，请先开始一场战斗。')
        return
    except error.combat.CombatRunningError:
        await combat_cmd.finish('❌ 当前战斗已经进入行动阶段。')
        return
    except error.combat.CombatOrderEmptyError:
        await combat_cmd.finish('❌ 先攻列表为空，无法进入行动阶段。')
        return


async def combat_next(bot: Bot, event: MessageEvent, state: T_State):
    combat: Combat = state['combat']
    try:
        await combat_ctl.next_combat_token(combat)
    except error.combat.CombatNotRunningError:
        await combat_cmd.finish('❌ 当前战斗并未处于行动阶段。')
        return
    except error.combat.CombatOrderEmptyError:
        await combat_cmd.finish('❌ 先攻列表为空，无法进入下一行动轮。')
        return


async def combat_end(bot: Bot, event: MessageEvent, state: T_State):
    combat: Combat = state['combat']
    try:
        await combat_ctl.end_combat(combat)
    except error.combat.CombatEndedError:
        await combat_cmd.finish('❌ 当前战斗已结束。')
        return


next_token = on_message(rule=regex(r'^\s*(回合结束|行动结束)\s*$'), permission=permission.GROUP, priority=99998, block=True)


@next_token.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    await prepare_combat_context(next_token, bot, event, state)
    combat: Combat = state['combat']
    if not combat or combat.state != CombatState.RUNNING:
        return
    is_gm: bool = state['is_gm']
    character: Optional[Character] = state['character']
    if not is_gm:
        if not character:
            return
        token = combat.tokens[combat.order.current_token_name]
        if token.character_id != character.id:
            return
    await combat_next(bot, event, state)


async def prepare_combat_context(matcher: Type[Matcher], bot: Bot, event: MessageEvent, state: T_State):
    is_prepared = await prepare_context(combat_cmd, bot, event, state)
    if not is_prepared:
        await matcher.finish()
        return
    room: Room = state['room']
    combat = await combat_ctl.get_room_running_combat(room)
    state['combat'] = combat


# DEPRECATED
battlestart = on_command('battlestart', block=True)


@battlestart.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    await battlestart.finish(f'「battlestart」指令已弃用。\n'
                             f'- 使用指令「{event.raw_message.strip()[0]}combat」切换到新的战斗轮指示器。')
