#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from nonebot import on_message, on_notice, Bot, on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Message, permission
from nonebot.adapters.onebot.v11.event import Event, MessageEvent, GroupRecallNoticeEvent
from nonebot.rule import regex
from nonebot.typing import T_State

from epicteller.bot.controller import base
from epicteller.core.controller import message as message_ctl
from epicteller.core.controller import episode as episode_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.core.model.character import Character
from epicteller.core.model.episode import Episode
from epicteller.core.model.message import TextMessageContent, ImageMessageContent, MessageContent
from epicteller.core.util import imghosting
from epicteller.core.util.enum import MessageType, ExternalType

VALID_MESSAGE_REGEX_PATTERN = r'^[^()（）]'
VALID_MESSAGE_REGEX = re.compile(VALID_MESSAGE_REGEX_PATTERN)

say = on_message(rule=regex(VALID_MESSAGE_REGEX_PATTERN), permission=permission.GROUP, priority=99999)


@say.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    await prepare(bot, event, state)
    episode: Episode = state.get('episode')
    character: Character = state.get('character')
    message_type: MessageType = state.get('message_type')
    content: MessageContent = state.get('content')
    is_gm: bool = state.get('is_gm')

    message = await message_ctl.create_message(episode, character, message_type, content, is_gm)
    internal_message_id = event.message_id
    base.message_cache[internal_message_id] = message.id


async def prepare(bot: Bot, event: MessageEvent, state: T_State):
    msg_text = event.get_plaintext().strip().replace('\r\n', '\n')
    if msg_text and VALID_MESSAGE_REGEX.search(msg_text):
        message_type = MessageType.TEXT
        content = TextMessageContent(text=msg_text)
    else:
        await say.finish()
        return
    is_prepared = await base.prepare_context(say, bot, event, state)
    if not is_prepared:
        await say.finish()
        return
    state['message_type'] = message_type
    state['content'] = content


image = on_command('image', aliases={'i'}, permission=permission.GROUP, block=True)


@image.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    is_prepared = await base.prepare_context(say, bot, event, state)
    if not is_prepared:
        await say.finish()
        return
    episode: Episode = state.get('episode')
    character: Character = state.get('character')
    is_gm: bool = state.get('is_gm')

    msg_images = [i for i in event.message if i.type == 'image']
    if not msg_images:
        await say.finish('🤔 需要上传一张图片哦。')
        return
    image_origin_url = msg_images[0].get('data', {}).get('url')
    if not image_origin_url:
        await say.finish('🤔 需要上传一张图片哦。')
        return
    image_token, width, height = await imghosting.upload_image_from_url(image_origin_url)
    content = ImageMessageContent(image=image_token, width=width, height=height)
    message = await message_ctl.create_message(episode, character, MessageType.IMAGE, content, is_gm)
    internal_message_id = event.message_id
    base.message_cache[internal_message_id] = message.id


async def recall_checker(e: Event) -> bool:
    return isinstance(e, GroupRecallNoticeEvent)


rollback = on_notice(recall_checker)


@rollback.handle()
async def _(bot: Bot, event: GroupRecallNoticeEvent, state: T_State):
    room_external_id = str(event.group_id)
    room = await room_ctl.get_room_by_external(ExternalType.QQ, room_external_id)
    if not room:
        return
    episode = await episode_ctl.get_room_running_episode(room)
    if not episode:
        return
    internal_id = event.message_id
    if internal_id not in base.message_cache:
        return
    message_id: int = base.message_cache[internal_id]
    message = await message_ctl.get_message(message_id)
    if not message or message.episode_id != episode.id:
        return
    await message_ctl.remove_message(message)
    content = message.content
    await rollback.finish(Message(f"🗑️ {MessageSegment.at(event.user_id)} 消息「{content.to_message()}」已删除。"))
