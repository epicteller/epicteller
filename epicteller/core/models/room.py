#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from typing import List, Optional

import base62
from sqlalchemy import select, and_

from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.seq import get_id


def _format_room(result) -> Optional[ObjectDict]:
    if not result:
        return None
    room = ObjectDict(
        id=result.id,
        url_token=result.url_token,
        name=result.name,
        description=result.description,
        is_removed=bool(result.is_removed),
        external_channel_id=result.external_channel_id,
        default_campaign_id=result.default_campaign_id,
        avatar=result.avatar,
        created=int(result.created),
    )
    return room


class Room:
    t = table.room
    select_clause = select([
        t.c.id,
        t.c.url_token,
        t.c.name,
        t.c.description,
        t.c.owner_id,
        t.c.is_removed,
        t.c.external_channel_id,
        t.c.default_campaign_id,
        t.c.avatar,
        t.c.created,
    ])

    @classmethod
    async def get_room_by_id(cls, room_id: int) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.id == room_id)
        result = await table.execute(query)
        return _format_room(await result.fetchone())

    @classmethod
    async def get_room_by_url_token(cls, url_token: str) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.url_token == url_token)
        result = await table.execute(query)
        return _format_room(await result.fetchone())

    @classmethod
    async def get_room_by_channel_id(cls, channel_id: str) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.external_channel_id == channel_id)
        result = await table.execute(query)
        return _format_room(await result.fetchone())

    @classmethod
    async def get_rooms_by_owner(cls, member_id: int) -> List[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.owner_id == member_id)
        results = await table.execute(query)
        rooms = [_format_room(room) for room in await results.fetchall()]
        return rooms

    @classmethod
    async def update_room(cls, room_id: int, **kwargs) -> None:
        if 'updated' not in kwargs:
            kwargs['updated'] = int(time.time())
        query = cls.t.update().values(kwargs).where(cls.t.c.id == room_id)
        await table.execute(query)

    @classmethod
    async def create_room(cls, name: str, description: str, owner_id: int,
                          channel_id: str, avatar: str='') -> ObjectDict:
        created = int(time.time())
        url_token = base62.encode(get_id())
        values = ObjectDict(
            url_token=url_token,
            name=name,
            description=description,
            owner_id=owner_id,
            is_removed=0,
            external_channel_id=channel_id,
            default_campaign_id=0,
            avatar=avatar,
            created=created,
            updated=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        room = _format_room(values)
        return room


class RoomMember:
    t = table.room_member

    @classmethod
    async def get_member_ids_by_room(cls, room_id: int, offset: int=0, limit: int=20) -> List[int]:
        query = select([cls.t.c.member_id]).where(cls.t.c.room_id == room_id).offset(offset).limit(limit)
        result = await table.execute(query)
        rows = await result.fetchall()
        member_ids = [row.member_id for row in rows]
        return member_ids

    @classmethod
    async def get_room_ids_by_member(cls, member_id: int, offset: int=0, limit: int=20) -> List[int]:
        query = select([cls.t.c.room_id]).where(cls.t.c.member_id == member_id).offset(offset).limit(limit)
        result = await table.execute(query)
        rows = await result.fetchall()
        room_ids = [row.room_id for row in rows]
        return room_ids

    @classmethod
    async def is_member_in_room(cls, room_id: int, member_id: int) -> bool:
        query = select([cls.t.c.id]).where(and_(cls.t.c.room_id == room_id, cls.t.c.member_id == member_id))
        result = await table.execute(query)
        row = await result.fetchone()
        return bool(row)

    @classmethod
    async def add_room_member(cls, room_id: int, member_id: int) -> None:
        if await cls.is_member_in_room(room_id, member_id):
            return
        created = int(time.time())
        query = cls.t.insert().values(room_id=room_id, member_id=member_id, created=created)
        await table.execute(query)

    @classmethod
    async def remove_member(cls, room_id: int, member_id: int) -> None:
        query = cls.t.delete().where(and_(cls.t.c.room_id == room_id, cls.t.c.member_id == member_id))
        await table.execute(query)


class RoomRunningEpisode:
    t = table.room_running_episode

    @classmethod
    async def get_running_episode_id(cls, room_id: int) -> Optional[int]:
        query = select([cls.t.c.episode_id]).where(cls.t.c.room_id == room_id)
        result = await table.execute(query)
        return await result.scalar()

    @classmethod
    async def set_running_episode(cls, room_id: int, episode_id: int) -> None:
        result = await cls.get_running_episode_id(room_id)
        if result:
            return
        query = cls.t.insert().values(room_id=room_id, episode_id=episode_id)
        await table.execute(query)

    @classmethod
    async def remove_running_episode(cls, room_id: int) -> None:
        query = cls.t.delete().where(cls.t.c.room_id == room_id)
        await table.execute(query)
