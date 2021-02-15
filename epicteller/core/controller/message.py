#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from typing import Optional, List, Iterable, Dict, Union

from epicteller.core import kafka
from epicteller.core.dao.message import MessageDAO
from epicteller.core.error.message import MessageCannotEditError
from epicteller.core.model.character import Character
from epicteller.core.model.episode import Episode
from epicteller.core.model.kafka_msg import message as message_msg
from epicteller.core.model.message import Message, MessageContent, TextMessageContent
from epicteller.core.util.enum import MessageType


async def get_message(message_id: Optional[int] = None, *,
                      url_token: Optional[str] = None) -> Optional[Message]:
    if message_id:
        return (await MessageDAO.batch_get_message_by_id([message_id])).get(message_id)
    if url_token:
        return (await MessageDAO.batch_get_message_by_url_token([url_token])).get(url_token)
    return None


async def batch_get_message(message_ids: Iterable[int] = None, *,
                            url_tokens: Iterable[str] = None) -> Dict[Union[int, str], Message]:
    if message_ids:
        return await MessageDAO.batch_get_message_by_id(message_ids)
    if url_tokens:
        return await MessageDAO.batch_get_message_by_url_token(url_tokens)
    return {}


async def get_episode_messages(episode_id: int, *,
                               before: Optional[int] = None, after: Optional[int] = None, around: Optional[int] = None,
                               limit: int = 40) -> List[Message]:
    if after is not None:
        return await MessageDAO.get_episode_messages_from_oldest(episode_id, after, limit)
    elif before is not None:
        return await MessageDAO.get_episode_messages_to_latest(episode_id, before, limit)
    elif around is not None:
        around_msg, before_msgs, after_msgs = await asyncio.gather(
            get_message(around),
            MessageDAO.get_episode_messages_to_latest(episode_id, around, limit),
            MessageDAO.get_episode_messages_from_oldest(episode_id, around, limit),
        )
        return [*before_msgs, around_msg, *after_msgs]
    return await MessageDAO.get_episode_latest_messages(episode_id, limit)


async def create_message(episode: Episode, character: Optional[Character], message_type: MessageType,
                         content: MessageContent, is_gm: bool = False) -> Message:
    if is_gm:
        character_id = 0
    else:
        character_id = character.id
    message = await MessageDAO.create_message(
        episode.campaign_id,
        episode.id,
        character_id,
        message_type,
        content.dict(),
        is_gm
    )
    await kafka.publish(message_msg.MsgMessageCreate(
        message_id=message.id,
        campaign_id=episode.campaign_id,
        episode_id=episode.id,
        character_id=character_id,
        is_gm=is_gm,
        content=content,
        type=message_type,
        created=message.created,
        updated=message.updated,
    ))
    return message


async def remove_message(message: Message):
    await MessageDAO.update_message(message.id, is_removed=1)
    await kafka.publish(message_msg.MsgMessageRemove(message_id=message.id))


async def recover_message(message: Message):
    await MessageDAO.update_message(message.id, is_removed=0)
    await kafka.publish(message_msg.MsgMessageRecover(message_id=message.id))


async def edit_text_message(message: Message, content: str):
    if message.type != MessageType.TEXT:
        raise MessageCannotEditError()
    msg_content = TextMessageContent(text=content)
    await MessageDAO.update_message(message.id, content=msg_content.dict())
    await kafka.publish(message_msg.MsgMessageEdit(
        message_id=message.id,
        content=msg_content,
    ))
