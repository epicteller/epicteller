#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot import on_command, CommandSession

from epicteller.bot.controller import base
from epicteller.core.controller import message as message_ctl
from epicteller.core.model.character import Character
from epicteller.core.model.episode import Episode
from epicteller.core.model.message import TextMessageContent, ImageMessageContent, MessageContent
from epicteller.core.util import imghosting
from epicteller.core.util.enum import MessageType


@on_command('say', only_to_me=False, privileged=True)
async def say(session: CommandSession):
    episode: Episode = session.get('episode')
    character: Character = session.get('character')
    message_type: MessageType = session.get('message_type')
    content: MessageContent = session.get('content')
    is_gm: bool = session.get('is_gm')

    await message_ctl.create_message(episode, character, message_type, content, is_gm)


@say.args_parser
async def _(session: CommandSession):
    is_prepared = await base.prepare_context(session)
    if not is_prepared:
        session.finish()
    msg_text = session.current_arg_text.strip()
    msg_images = session.current_arg_images
    if msg_text:
        message_type = MessageType.TEXT
        content = TextMessageContent(text=msg_text)
    elif msg_images:
        message_type = MessageType.IMAGE
        image_origin_url = msg_images[0]
        image_token = await imghosting.upload_image_from_url(image_origin_url)
        content = ImageMessageContent(image=image_token)
    else:
        session.finish()
        return
    session.state['message_type'] = message_type
    session.state['content'] = content
