#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional, List, Tuple

import nonebot
from nonebot.adapters.cqhttp import Bot, MessageSegment
from nonebot.adapters.cqhttp import Message

from epicteller.bot import bus
from epicteller.bot.controller import combat as combat_bot_ctl
from epicteller.core.controller import character as character_ctl
from epicteller.core.controller import combat as combat_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.core.model.combat import Combat
from epicteller.core.model.kafka_msg.combat import MsgCombat, MsgCombatRun, MsgCombatEnd, MsgCombatActingTokenChange, \
    MsgCombatReorderToken, MsgAddCombatToken, MsgRemoveCombatToken
from epicteller.core.model.room import Room
from epicteller.core.util.enum import ExternalType, CombatState


@dataclass
class CombatContext:
    bot: Bot
    combat: Combat
    room: Room
    room_external_id: str
    bot_id: str

    async def send(self, message: Message):
        group_id = int(self.room_external_id)
        self_id = int(self.bot_id)
        await self.bot.send_group_msg(group_id=group_id, message=message, self_id=self_id)


async def prepare_context(msg: MsgCombat) -> Optional[CombatContext]:
    combat_id = msg.combat_id
    combat = await combat_ctl.get_combat(combat_id)
    room = await room_ctl.get_room(combat.room_id)
    room_external_info = await room_ctl.get_room_external_info(room.id, ExternalType.QQ)
    bot_id = room_external_info.bot_id
    bots = nonebot.get_bots()
    if bot_id not in bots:
        return
    bot = bots[bot_id]
    context = CombatContext(
        bot=bot,
        combat=combat,
        room=room,
        room_external_id=room_external_info.external_id,
        bot_id=bot_id,
    )
    return context


@bus.on('epicteller.combat.run')
async def combat_run(topic: str, data: str):
    msg = MsgCombatRun.parse_raw(data)
    context = await prepare_context(msg)
    if not context:
        return
    combat = context.combat
    token = combat.tokens[combat.order.current_token_name]
    player_name = await combat_bot_ctl.format_token_message(token)
    message = Message(f'⚔️进入行动阶段。\n'
                      f'第 {combat.order.round_count} 回合开始，'
                      f'进入{player_name}的行动轮。')
    await context.send(message)


@bus.on('epicteller.combat.end')
async def combat_end(topic: str, data: str):
    msg = MsgCombatEnd.parse_raw(data)
    context = await prepare_context(msg)
    if not context:
        return
    await context.send(Message('战斗结束，战斗轮指示器已关闭。'))


@bus.on('epicteller.combat.acting_token_change')
async def combat_acting_token_change(topic: str, data: str):
    msg = MsgCombatActingTokenChange.parse_raw(data)
    context = await prepare_context(msg)
    if not context:
        return
    combat = context.combat
    if combat.state == CombatState.ENDED:
        return
    round_start_msg = f'第 {context.combat.order.round_count} 回合开始，' if msg.is_next_round else ''
    token = combat.tokens[combat.order.current_token_name]
    player_name = await combat_bot_ctl.format_token_message(token)
    message = Message(f'{round_start_msg}进入{player_name}的行动轮。')
    await context.send(message)


@bus.on('epicteller.combat.reorder_token')
async def reorder_token(topic: str, data: str):
    msg = MsgCombatReorderToken.parse_raw(data)
    context = await prepare_context(msg)
    if not context:
        return
    combat = context.combat
    if combat.state == CombatState.ENDED:
        return
    last_order = msg.last_order_list
    current_order = msg.current_order_list
    if last_order == current_order:
        return
    if set(last_order) != set(current_order):
        return
    changed_detail: List[Tuple[str, int, int]] = []
    for token_name in current_order:
        last_rank = last_order.index(token_name)
        current_rank = current_order.index(token_name)
        if last_rank == current_rank:
            continue
        changed_detail.append((token_name, last_rank, current_rank))
    if not changed_detail:
        return
    messages = ['战斗的先攻顺序被变更。\n']
    for detail in changed_detail:
        token_name, last_rank, current_rank = detail
        token = combat.tokens[token_name]
        player_name = await combat_bot_ctl.format_token_message(token)
        if current_rank < last_rank:
            delta = f'前移 {last_rank - current_rank} 位'
        elif last_rank < current_rank:
            delta = f'后移 {current_rank - last_rank} 位'
        else:
            continue
        messages.append(f' - {player_name}{delta}，目前处于第 {current_rank + 1} 位。\n')
    await context.send(Message(messages))


@bus.on('epicteller.combat.add_combat_token')
async def add_combat_token(topic: str, data: str):
    msg = MsgAddCombatToken.parse_raw(data)
    context = await prepare_context(msg)
    if not context:
        return
    combat = context.combat
    if combat.state == CombatState.ENDED:
        return
    token = msg.token
    player_name = await combat_bot_ctl.format_token_message(token)
    message = Message(f'{player_name} 已计入先攻顺位，目前位于第 {msg.rank + 1} 位。')
    await context.send(message)


@bus.on('epicteller.combat.remove_combat_token')
async def remove_combat_token(topic: str, data: str):
    msg = MsgRemoveCombatToken.parse_raw(data)
    context = await prepare_context(msg)
    if not context:
        return
    combat = context.combat
    if combat.state == CombatState.ENDED:
        return
    token = msg.token
    player_name = await combat_bot_ctl.format_token_message(token)
    message = Message(f'{player_name} 的先攻顺位被移除。')
    await context.send(message)
