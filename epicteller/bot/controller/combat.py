#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot.adapters.onebot.v11 import escape

from epicteller.core.controller import character as character_ctl
from epicteller.core.model.combat import CombatToken, Combat
from nonebot.adapters.onebot.v11.message import Message, MessageSegment

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


async def format_combat_xml(combat: Combat) -> str:
    data = r'''
    <?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID="1" templateID="123" action="web" brief="[战斗] 战斗状态" sourceMsgId="0" url="https://www.epicteller.com/combat/{url_token}" flag="0" adverSign="0" multiMsgFlag="0"><item layout="2" advertiser_id="0" aid="0"><picture cover="https://ep-predict.epicteller.com/icon512.png" w="0" h="0" /><title>战斗状态</title><summary>战斗状态</summary></item><source name="" icon="" action="" appid="-1" /></msg>
        '''.format(url_token=combat.url_token)
    return escape(data)
