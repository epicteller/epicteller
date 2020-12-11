#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot import Bot
from nonebot.typing import Matcher, Event

from epicteller.core.controller import campaign as campaign_ctl
from epicteller.core.controller import character as character_ctl
from epicteller.core.controller import episode as episode_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.core.tables import table
from epicteller.core.util.enum import ExternalType


async def prepare_context(matcher: Matcher, bot: Bot, event: Event, state: dict) -> bool:
    if event.detail_type != 'group' or event.raw_event['anonymous']:
        return False
    room_external_id = str(event.group_id)
    member_external_id = str(event.user_id)
    name = event.sender['card'] or event.sender['nickname']

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

    if not character:
        async with table.db.begin():
            character = await character_ctl.create_character(campaign, name, member, '', '')
            await character_ctl.bind_character_external(character, ExternalType.QQ, member_external_id)
    elif not member:
        if not await character_ctl.check_character_external(character, ExternalType.QQ, member_external_id):
            await matcher.finish(f'冒充其他用户的角色')
    else:
        if not character.member_id:
            await character_ctl.bind_character_member(character, member)
        elif character.member_id != member.id:
            await matcher.finish(f'冒充其他用户的角色')

    state['is_gm'] = False
    return True
