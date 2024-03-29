#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Type

from lru import LRU
from nonebot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, MessageEvent
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from epicteller.core.controller import campaign as campaign_ctl
from epicteller.core.controller import character as character_ctl
from epicteller.core.controller import episode as episode_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.core.tables import table
from epicteller.core.util.enum import ExternalType

message_cache = LRU(10000)


async def prepare_context(matcher: Type[Matcher], bot: Bot, event: MessageEvent, state: T_State) -> bool:
    if event.get_event_name() != 'message.group.normal':
        return False
    assert isinstance(event, GroupMessageEvent)
    room_external_id = str(event.group_id)
    member_external_id = str(event.user_id)
    name = event.sender.card or event.sender.nickname

    room = await room_ctl.get_room_by_external(ExternalType.QQ, room_external_id)
    if not room:
        return False
    state['room'] = room
    episode = await episode_ctl.get_room_running_episode(room)
    if not episode:
        return False
    state['episode'] = episode
    campaign = await campaign_ctl.get_campaign(episode.campaign_id)
    character = await character_ctl.get_character_by_campaign_name(campaign, name)
    state['character'] = character
    member = await member_ctl.get_member_by_external(ExternalType.QQ, member_external_id)
    if member and member.id == campaign.owner_id:
        state['is_gm'] = True
        return True
    is_room_member = member and await room_ctl.is_room_member(room.id, member.id)

    if room.is_locked and not is_room_member:
        return False

    if not character:
        async with table.db.begin():
            character = await character_ctl.create_character(name, member)
            await character_ctl.bind_character_external(character, ExternalType.QQ, member_external_id)
            await character_ctl.bind_character_campaign(character, campaign)
            state['character'] = character
    elif not member:
        if not await character_ctl.check_character_external(character, ExternalType.QQ, member_external_id):
            await matcher.finish(f'冒充其他用户的角色')
    else:
        if not character.member_id:
            await character_ctl.bind_character_member(character, member)
        elif character.member_id != member.id:
            await matcher.finish(f'冒充其他用户的角色')

    state['is_gm'] = False
    if not room.is_locked and member and not is_room_member:
        await room_ctl.add_room_member(room.id, member.id)
    return True
