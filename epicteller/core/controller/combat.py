#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from typing import Optional, Iterable, Dict, Union, Tuple, List

from epicteller.core import error, kafka
from epicteller.core.controller import episode as episode_ctl
from epicteller.core.dao.combat import CombatDAO, RoomRunningCombatDAO
from epicteller.core.dao.room import RoomRunningEpisodeDAO
from epicteller.core.model.combat import Combat, CombatToken
from epicteller.core.model.kafka_msg import combat as combat_msg
from epicteller.core.model.room import Room
from epicteller.core.tables import table
from epicteller.core.util.enum import CombatState


async def get_combat(combat_id: Optional[int]=None, *,
                     url_token: Optional[str]=None) -> Optional[Combat]:
    if combat_id:
        return (await CombatDAO.batch_get_combat_by_id([combat_id])).get(combat_id)
    elif url_token:
        return (await CombatDAO.batch_get_combat_by_url_token([url_token])).get(url_token)
    return None


async def batch_get_combat(combat_ids: Iterable[int]=None, *,
                           url_tokens: Iterable[str]=None) -> Dict[Union[int, str], Combat]:
    if combat_ids:
        return await CombatDAO.batch_get_combat_by_id(combat_ids)
    elif url_tokens:
        return await CombatDAO.batch_get_combat_by_url_token(url_tokens)
    return {}


async def get_room_running_combat(room: Room) -> Optional[Combat]:
    running_combat_id = await RoomRunningCombatDAO.get_running_combat_id(room.id)
    if not running_combat_id:
        return
    return await get_combat(running_combat_id)


async def start_new_combat(room: Room) -> Combat:
    running_combat_id = await RoomRunningCombatDAO.get_running_combat_id(room.id)
    if running_combat_id:
        raise error.combat.CombatRunningError()
    running_episode_id = await RoomRunningEpisodeDAO.get_running_episode_id(room.id)
    if not running_episode_id:
        raise error.episode.EpisodeNotRunningError()
    episode = await episode_ctl.get_episode(running_episode_id)
    campaign_id = episode.campaign_id
    async with table.db.begin():
        combat = await CombatDAO.create_combat(room.id, campaign_id)
        await RoomRunningCombatDAO.set_running_combat(room.id, combat.id)
    await kafka.publish(combat_msg.MsgCombatCreate(combat_id=combat.id))
    return combat


async def end_combat(combat: Combat):
    if not combat or combat.state == CombatState.ENDED:
        raise error.combat.CombatEndedError()
    running_combat_id = await RoomRunningCombatDAO.get_running_combat_id(combat.room_id)
    async with table.db.begin():
        combat.state = CombatState.ENDED
        await CombatDAO.update_combat(combat.id,
                                      state=int(CombatState.ENDED),
                                      ended_at=int(time.time()))
        if running_combat_id == combat.id:
            await RoomRunningCombatDAO.remove_running_combat(combat.room_id)
    await kafka.publish(combat_msg.MsgCombatEnd(combat_id=combat.id))


async def run_combat(combat: Combat):
    if not combat or combat.state == CombatState.ENDED:
        raise error.combat.CombatEndedError()
    elif combat.state == CombatState.RUNNING:
        raise error.combat.CombatRunningError()
    if not combat.order.order_list:
        raise error.combat.CombatOrderEmptyError()
    combat.order.current_token_name = combat.order.order_list[0]
    combat.order.round_count = 1
    combat.state = CombatState.RUNNING
    await CombatDAO.update_combat(combat.id, order=combat.order.dict(), state=int(CombatState.RUNNING))
    await kafka.publish(combat_msg.MsgCombatRun(combat_id=combat.id))


async def next_combat_token(combat: Combat) -> Tuple[int, CombatToken]:
    if not combat or combat.state != CombatState.RUNNING:
        raise error.combat.CombatNotRunningError()
    order_list = combat.order.order_list
    if not order_list:
        raise error.combat.CombatOrderEmptyError()
    current_token_name = combat.order.current_token_name
    # 正常情况下不会有这种情况
    if not current_token_name or current_token_name not in order_list:
        current_token_name = order_list[0]
        return combat.order.round_count, combat.tokens[current_token_name]
    last_token_name = current_token_name
    order_index = order_list.index(current_token_name)
    is_next_round = False
    # 最后一个了，回合数 + 1
    if order_index == len(order_list) - 1:
        rank = 0
        combat.order.round_count += 1
        is_next_round = True
    else:
        rank = order_index + 1
    current_token_name = order_list[rank]
    combat.order.current_token_name = current_token_name
    await CombatDAO.update_combat(combat.id, order=combat.order.dict())
    await kafka.publish(combat_msg.MsgCombatActingTokenChange(
        combat_id=combat.id,
        last_token_name=last_token_name,
        current_token_name=current_token_name,
        round_count=combat.order.round_count,
        is_next_round=is_next_round,
        rank=rank,
    ))
    return rank, combat.tokens[current_token_name]


async def set_current_token(combat: Combat, token: CombatToken):
    assert token.name in combat.order.order_list and token.name in combat.tokens
    if token.name == combat.order.current_token_name:
        return
    last_token_name = combat.order.current_token_name
    combat.order.current_token_name = token.name
    rank = combat.order.order_list.index(token.name)
    await CombatDAO.update_combat(combat.id, order=combat.order.dict())
    await kafka.publish(combat_msg.MsgCombatActingTokenChange(
        combat_id=combat.id,
        last_token_name=last_token_name,
        current_token_name=token.name,
        round_count=combat.order.round_count,
        rank=rank,
    ))


async def reorder_tokens(combat: Combat, token_names: List[str]) -> Combat:
    if set(token_names) != set(combat.order.order_list):
        raise error.combat.CombatTokenChangedError()
    if token_names == combat.order.order_list:
        return combat
    last_order_list = combat.order.order_list.copy()
    combat.order.order_list = token_names
    await CombatDAO.update_combat(combat.id, order=combat.order.dict())
    await kafka.publish(combat_msg.MsgCombatReorderToken(
        combat_id=combat.id,
        last_order_list=last_order_list,
        current_order_list=token_names,
    ))
    return combat


async def add_combat_token(combat: Combat, token: CombatToken) -> int:
    if token.name in combat.tokens or token.name in combat.order.order_list:
        raise error.combat.CombatTokenAlreadyExistsError()
    combat.tokens[token.name] = token
    combat.order.order_list.append(token.name)
    # 先攻模式下，顺序强制按照先攻值降序排列
    if combat.state == CombatState.INITIATING:
        combat.order.order_list.sort(key=lambda name: combat.tokens[name].initiative, reverse=True)
    rank = combat.order.order_list.index(token.name)
    # 确保 token map 和先攻顺序数据一致性
    assert set(combat.tokens.keys()) == set(combat.order.order_list)
    tokens = {name: token.dict() for name, token in combat.tokens.items()}
    await CombatDAO.update_combat(combat.id, tokens=tokens, order=combat.order.dict())
    await kafka.publish(combat_msg.MsgAddCombatToken(
        combat_id=combat.id,
        token=token,
        rank=rank,
    ))
    return rank


async def remove_combat_token(combat: Combat, token_name: str):
    if len(combat.order.order_list) <= 1:
        raise error.combat.CombatOrderEmptyError()
    if combat.order.current_token_name == token_name:
        raise error.combat.CannotRemoveActingTokenError()
    token = combat.tokens[token_name].copy()
    del combat.tokens[token_name]
    combat.order.order_list.remove(token_name)
    # 确保 token map 和先攻顺序数据一致性
    assert set(combat.tokens.keys()) == set(combat.order.order_list)
    tokens = {name: token.dict() for name, token in combat.tokens.items()}
    await CombatDAO.update_combat(combat.id, tokens=tokens, order=combat.order.dict())
    await kafka.publish(combat_msg.MsgRemoveCombatToken(
        combat_id=combat.id,
        token=token,
    ))
