#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot import CommandSession

from epicteller.core.controller import campaign as campaign_ctl
from epicteller.core.controller import character as character_ctl
from epicteller.core.controller import episode as episode_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.core.tables import table
from epicteller.core.util.enum import ExternalType


async def prepare_context(session: CommandSession) -> bool:
    if session.event.detail_type != 'group' or session.event.anonymous is not None:
        return False
    room_external_id = str(session.event.group_id)
    member_external_id = str(session.event.user_id)
    name = session.event.sender['nickname']

    room = await room_ctl.get_room_by_external(ExternalType.QQ, room_external_id)
    if not room:
        return False
    session.state['room'] = room
    episode = await episode_ctl.get_room_running_episode(room)
    if not episode:
        return False
    session.state['episode'] = episode
    campaign = await campaign_ctl.get_campaign(episode.campaign_id)
    character = await character_ctl.get_character_by_campaign_name(campaign, name)
    session.state['character'] = character
    member = await member_ctl.get_member_by_external(ExternalType.QQ, member_external_id)
    if member and member.id == campaign.owner_id:
        session.state['is_gm'] = True
        return True

    if not character:
        async with table.db.begin():
            character = await character_ctl.create_character(campaign, name, member, '', '')
            await character_ctl.bind_character_external(character, ExternalType.QQ, member_external_id)
    elif not member:
        if not await character_ctl.check_character_external(character, ExternalType.QQ, member_external_id):
            session.finish(f'冒充其他用户的角色')
    else:
        if not character.member_id:
            await character_ctl.bind_character_member(character, member)
        elif character.member_id != member.id:
            session.finish(f'冒充其他用户的角色')

    session.state['is_gm'] = False
    return True
