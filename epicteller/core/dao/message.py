#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from typing import List, Optional, Iterable, Dict

import base62
from sqlalchemy import select, and_, desc

from epicteller.core.model.message import Message, TextMessageContent, ImageMessageContent, DiceMessageContent, \
    MessageContent
from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.enum import MessageType
from epicteller.core.util.seq import get_id


def _format_message(result) -> Optional[Message]:
    if not result:
        return None
    message_type = MessageType(result.type)
    if message_type == MessageType.TEXT:
        content = TextMessageContent.parse_obj(result.content)
    elif message_type == MessageType.IMAGE:
        content = ImageMessageContent.parse_obj(result.content)
    elif message_type == MessageType.DICE:
        content = DiceMessageContent.parse_obj(result.content)
    else:
        content = MessageContent()
    message = Message(
        id=result.id,
        url_token=result.url_token,
        episode_id=result.episode_id,
        character_id=result.character_id,
        type=MessageType(result.type),
        is_removed=bool(result.is_removed),
        is_gm=bool(result.is_gm),
        content=content,
        created=result.created,
        updated=result.updated,
    )
    return message

    
class MessageDAO:
    t = table.message
    
    select_clause = select([
        t.c.id,
        t.c.url_token,
        t.c.episode_id,
        t.c.character_id,
        t.c.type,
        t.c.is_removed,
        t.c.is_gm,
        t.c.content,
        t.c.created,
        t.c.updated,
    ])
    
    @classmethod
    async def batch_get_message_by_id(cls, message_ids: Iterable[int]) -> Dict[int, Message]:
        query = cls.select_clause.where(cls.t.c.id.in_(message_ids))
        result = await table.execute(query)
        rows = await result.fetchall()
        return {row.id: _format_message(row) for row in rows}

    @classmethod
    async def batch_get_message_by_url_token(cls, url_tokens: Iterable[str]) -> Dict[str, Message]:
        query = cls.select_clause.where(cls.t.c.url_token.in_(url_tokens))
        result = await table.execute(query)
        rows = await result.fetchall()
        return {row.url_token: _format_message(row) for row in rows}

    @classmethod
    async def get_episode_latest_messages(cls, episode_id: int, limit: int) -> List[Message]:
        query = cls.select_clause.where(and_(
            cls.t.c.episode_id == episode_id,
            cls.t.c.is_removed == 0,
        )).order_by(desc(cls.t.c.id)).limit(limit)
        results = await table.execute(query)
        messages = [_format_message(result) for result in await results.fetchall()]
        messages.reverse()
        return messages

    @classmethod
    async def get_episode_messages_from_oldest(cls, episode_id: int, oldest: int, limit: int) -> List[Message]:
        query = cls.select_clause.where(and_(
            cls.t.c.episode_id == episode_id,
            cls.t.c.is_removed == 0,
            cls.t.c.id > oldest,
        )).limit(limit)
        results = await table.execute(query)
        messages = [_format_message(result) for result in await results.fetchall()]
        return messages

    @classmethod
    async def get_episode_messages_to_latest(cls, episode_id: int, latest: int, limit: int) -> List[Message]:
        query = cls.select_clause.where(and_(
            cls.t.c.episode_id == episode_id,
            cls.t.c.is_removed == 0,
            cls.t.c.id < latest,
        )).order_by(desc(cls.t.c.id)).limit(limit)
        results = await table.execute(query)
        messages = [_format_message(result) for result in await results.fetchall()]
        messages.reverse()
        return messages

    @classmethod
    async def update_message(cls, message_id: int, **kwargs) -> None:
        if 'updated' not in kwargs:
            kwargs['updated'] = int(time.time())
        query = cls.t.update().values(kwargs).where(cls.t.c.id == message_id)
        await table.execute(query)

    @classmethod
    async def create_message(cls, episode_id: int, character_id: int, message_type: MessageType,
                             content: dict, is_gm: bool, created: Optional[int] = None) -> Message:
        url_token = base62.encode(get_id())
        if not created:
            created = int(time.time())
        values = ObjectDict(
            url_token=url_token,
            episode_id=episode_id,
            character_id=character_id,
            type=int(message_type),
            is_removed=0,
            is_gm=int(is_gm),
            content=content,
            created=created,
            updated=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        message = _format_message(values)
        return message
