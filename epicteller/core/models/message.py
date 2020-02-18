#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from typing import List, Optional

import base62
from sqlalchemy import select, and_

from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.const import MessageType
from epicteller.core.util.seq import get_id


def _format_message(result) -> Optional[ObjectDict]:
    if not result:
        return None
    message = ObjectDict(
        id=result.id,
        url_token=result.url_token,
        episode_id=result.episode_id,
        character_id=result.character_id,
        type=MessageType(result.type),
        is_removed=bool(result.is_removed),
        content=result.content,
        dice_id=result.dice_id if result.dice_id else None,
        created=result.created,
        updated=result.updated,
    )
    return message

    
class Message:
    t = table.message
    
    select_clause = select([
        t.c.id,
        t.c.url_token,
        t.c.episode_id,
        t.c.character_id,
        t.c.type,
        t.c.is_removed,
        t.c.content,
        t.c.dice_id,
        t.c.created,
        t.c.updated,
    ])
    
    @classmethod
    async def get_message_by_id(cls, message_id: int) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.id == message_id)
        result = await table.execute(query)
        return _format_message(await result.fetchone())

    @classmethod
    async def get_message_by_url_token(cls, url_token: str) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.url_token == url_token)
        result = await table.execute(query)
        return _format_message(await result.fetchone())

    @classmethod
    async def get_episode_messages(cls, episode_id: int, start: int, limit: int) -> List[ObjectDict]:
        query = cls.select_clause.where(and_(
            cls.t.c.episode_id == episode_id,
            cls.t.c.is_removed == 0,
            cls.t.c.id > start,
        )).limit(limit)
        return query

    @classmethod
    async def update_message(cls, message_id: int, **kwargs) -> None:
        if 'updated' not in kwargs:
            kwargs['updated'] = int(time.time())
        query = cls.t.update().values(kwargs).where(cls.t.c.id == message_id)
        await table.execute(query)

    @classmethod
    async def create_message(cls, episode_id: int, character_id: int, message_type: MessageType,
                             content: str, dice_id: Optional[int]=None) -> ObjectDict:
        created = int(time.time())
        url_token = base62.encode(get_id())
        values = ObjectDict(
            url_token=url_token,
            episode_id=episode_id,
            character_id=character_id,
            type=int(message_type),
            is_removed=0,
            content=content,
            dice_id=dice_id or 0,
            created=created,
            updated=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        message = _format_message(values)
        return message
