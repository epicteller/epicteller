#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from typing import List, Optional, Iterable, Dict

import base62
from sqlalchemy import select, and_

from epicteller.core.model.room import Room, RoomExternalInfo
from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.enum import ExternalType
from epicteller.core.util.seq import get_id


def _format_room(result) -> Optional[Room]:
    if not result:
        return None
    room = Room(
        id=result.id,
        url_token=result.url_token,
        name=result.name,
        description=result.description,
        is_removed=bool(result.is_removed),
        current_campaign_id=result.current_campaign_id or None,
        avatar=result.avatar,
        created=int(result.created),
        updated=int(result.updated),
    )
    return room


class RoomDAO:
    t = table.room
    select_clause = select([
        t.c.id,
        t.c.url_token,
        t.c.name,
        t.c.description,
        t.c.owner_id,
        t.c.is_removed,
        t.c.current_campaign_id,
        t.c.avatar,
        t.c.created,
        t.c.updated,
    ])

    @classmethod
    async def batch_get_room_by_id(cls, room_ids: Iterable[int]) -> Dict[int, Room]:
        query = cls.select_clause.where(cls.t.c.id.in_(room_ids))
        result = await table.execute(query)
        rows = await result.fetchall()
        return {row.id: _format_room(row) for row in rows}

    @classmethod
    async def batch_get_room_by_url_token(cls, url_tokens: Iterable[str]) -> Dict[str, Room]:
        query = cls.select_clause.where(cls.t.c.url_token.in_(url_tokens))
        result = await table.execute(query)
        rows = await result.fetchall()
        return {row.url_token: _format_room(row) for row in rows}

    @classmethod
    async def get_rooms_by_owner(cls, member_id: int) -> List[Room]:
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
    async def create_room(cls, name: str, description: str, owner_id: int, avatar: str = '') -> Room:
        created = int(time.time())
        url_token = base62.encode(get_id())
        values = ObjectDict(
            url_token=url_token,
            name=name,
            description=description,
            owner_id=owner_id,
            is_removed=0,
            current_campaign_id=0,
            avatar=avatar,
            created=created,
            updated=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        room = _format_room(values)
        return room


class RoomMemberDAO:
    t = table.room_member

    @classmethod
    async def get_member_ids_by_room(cls, room_id: int, offset: int = 0, limit: int = 20) -> List[int]:
        query = select([cls.t.c.member_id]).where(cls.t.c.room_id == room_id).offset(offset).limit(limit)
        result = await table.execute(query)
        rows = await result.fetchall()
        member_ids = [row.member_id for row in rows]
        return member_ids

    @classmethod
    async def get_room_ids_by_member(cls, member_id: int, offset: int = 0, limit: int = 20) -> List[int]:
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


class RoomRunningEpisodeDAO:
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


class RoomExternalDAO:
    t = table.room_external_id

    @classmethod
    async def get_room_id_by_external(cls, external_type: ExternalType, external_id: str) -> Optional[int]:
        query = select([cls.t.c.room_id]).where(and_(cls.t.c.type == int(external_type),
                                                     cls.t.c.external_id == external_id))
        result = await table.execute(query)
        room_id = await result.scalar()
        return room_id

    @classmethod
    async def get_external_infos_by_room(cls, room_id: int) -> Dict[ExternalType, RoomExternalInfo]:
        query = select([
            cls.t.c.type,
            cls.t.c.external_id,
            cls.t.c.bot_id,
        ]).where(cls.t.c.room_id == room_id)
        result = await table.execute(query)
        rows = await result.fetchall()
        externals = {ExternalType(row.type): RoomExternalInfo(room_id=room_id,
                                                              type=ExternalType(row.type),
                                                              external_id=row.external_id,
                                                              bot_id=row.bot_id) for row in rows}
        return externals

    @classmethod
    async def bind_room_external_id(cls, room_id: int, external_type: ExternalType, external_id: str,
                                    bot_id: str) -> None:
        query = cls.t.insert().values(
            room_id=room_id,
            type=int(external_type),
            external_id=external_id,
            bot_id=bot_id,
        )
        await table.execute(query)

    @classmethod
    async def unbind_room_external_id(cls, room_id: int, external_type: ExternalType) -> None:
        query = cls.t.delete().where(and_(cls.t.c.room_id == room_id, cls.t.c.type == int(external_type)))
        await table.execute(query)
