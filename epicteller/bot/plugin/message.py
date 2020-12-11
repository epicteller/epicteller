#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot import on_message, Bot
from nonebot.typing import Event
from nonebot.rule import regex

from epicteller.bot.controller import base
from epicteller.core.controller import message as message_ctl
from epicteller.core.model.character import Character
from epicteller.core.model.episode import Episode
from epicteller.core.model.message import TextMessageContent, ImageMessageContent, MessageContent
from epicteller.core.util import imghosting
from epicteller.core.util.enum import MessageType


say = on_message(rule=regex(r'^[^()（）]'), priority=99999)


@say.handle()
async def _(bot: Bot, event: Event, state: dict):
    await prepare(bot, event, state)
    episode: Episode = state.get('episode')
    character: Character = state.get('character')
    message_type: MessageType = state.get('message_type')
    content: MessageContent = state.get('content')
    is_gm: bool = state.get('is_gm')

    await message_ctl.create_message(episode, character, message_type, content, is_gm)


async def prepare(bot: Bot, event: Event, state: dict):
    is_prepared = await base.prepare_context(say, bot, event, state)
    if not is_prepared:
        await say.finish()
    msg_text = event.plain_text.strip()
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
