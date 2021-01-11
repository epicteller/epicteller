#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lru import LRU
from nonebot import on_message, on_notice, Bot
from nonebot.adapters.cqhttp import MessageSegment, Message
from nonebot.adapters.cqhttp.event import MessageEvent, GroupRecallNoticeEvent
from nonebot.rule import regex

from epicteller.bot.controller import base
from epicteller.core.controller import message as message_ctl
from epicteller.core.controller import episode as episode_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.core.model.character import Character
from epicteller.core.model.episode import Episode
from epicteller.core.model.message import TextMessageContent, ImageMessageContent, MessageContent
from epicteller.core.util import imghosting
from epicteller.core.util.enum import MessageType, ExternalType


message_cache = LRU(10000)


say = on_message(rule=regex(r'^[^()（）]'), priority=99999)


@say.handle()
async def _(bot: Bot, event: MessageEvent, state: dict):
    await prepare(bot, event, state)
    episode: Episode = state.get('episode')
    character: Character = state.get('character')
    message_type: MessageType = state.get('message_type')
    content: MessageContent = state.get('content')
    is_gm: bool = state.get('is_gm')

    message = await message_ctl.create_message(episode, character, message_type, content, is_gm)
    internal_message_id = event.message_id
    message_cache[internal_message_id] = message.id


async def prepare(bot: Bot, event: MessageEvent, state: dict):
    is_prepared = await base.prepare_context(say, bot, event, state)
    if not is_prepared:
        await say.finish()
    msg_text = event.get_plaintext().strip().replace('\r\n', '\n')
    msg_images = [i for i in event.message if i.type == 'image']
    if msg_text:
        message_type = MessageType.TEXT
        content = TextMessageContent(text=msg_text)
    elif msg_images:
        message_type = MessageType.IMAGE
        image_origin_url = msg_images[0]['data']['url']
        image_token = await imghosting.upload_image_from_url(image_origin_url)
        content = ImageMessageContent(image=image_token)
    else:
        await say.finish()
        return
    state['message_type'] = message_type
    state['content'] = content


rollback = on_notice(lambda b, e, d: e.notice_type == 'group_recall')


@rollback.handle()
async def _(bot: Bot, event: GroupRecallNoticeEvent, state: dict):
    room_external_id = str(event.group_id)
    room = await room_ctl.get_room_by_external(ExternalType.QQ, room_external_id)
    if not room:
        return
    episode = await episode_ctl.get_room_running_episode(room)
    if not episode:
        return
    internal_id = event.message_id
    if internal_id not in message_cache:
        return
    message_id = message_cache[internal_id]
    message = await message_ctl.get_message(message_id)
    if not message or message.episode_id != episode.id:
        return
    await message_ctl.remove_message(message_id)
    content = message.content
    await rollback.finish(Message(f"🗑️ {MessageSegment.at(event.user_id)} 消息「{content.to_message()}」已删除。"))
