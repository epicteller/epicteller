#!/usr/bin/env python
# -*- coding: utf-8 -*-
from epicteller.core.controller import character as character_ctl
from epicteller.core.model.combat import CombatToken
from nonebot.adapters.cqhttp.message import Message, MessageSegment

from epicteller.core.util.enum import ExternalType


async def format_token_message(token: CombatToken) -> Message:
    default_msg = Message(f'「{token.name}」')
    if not token.character_id:
        return default_msg
    character = await character_ctl.get_character(token.character_id)
    if not character:
        return default_msg
    external_id = await character_ctl.get_character_external_id(character.id, ExternalType.QQ)
    if not external_id:
        return default_msg
    if character.name == token.name:
        return Message(MessageSegment.at(external_id))
    return Message(f'「{token.name}」(控制者：{MessageSegment.at(external_id)})')
