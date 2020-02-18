#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from typing import List, Optional

import base62
from sqlalchemy import select

from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.seq import get_id


def _format_character(result) -> Optional[ObjectDict]:
    if not result:
        return
    character = ObjectDict(
        id=result.id,
        url_token=result.url_token,
        member_id=result.member_id,
        campaign_id=result.campaign_id,
        name=result.name,
        avatar=result.avatar,
        description=result.description,
        is_removed=bool(result.is_removed),
        data=result.data,
        created=result.created,
        updated=result.updated,
    )
    return character


class Character:
    t = table.character
    select_clause = select([
        t.c.id,
        t.c.url_token,
        t.c.name,
        t.c.member_id,
        t.c.campaign_id,
        t.c.avatar,
        t.c.description,
        t.c.is_removed,
        t.c.data,
        t.c.created,
        t.c.updated,
    ])

    @classmethod
    async def get_character_by_id(cls, character_id: int) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.id == character_id)
        result = await table.execute(query)
        return _format_character(await result.fetchone())

    @classmethod
    async def get_character_by_url_token(cls, url_token: str) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.url_token == url_token)
        result = await table.execute(query)
        return _format_character(await result.fetchone())

    @classmethod
    async def get_characters_by_campaign_id(cls, campaign_id: str) -> List[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.campaign_id == campaign_id)
        results = await table.execute(query)
        characters = [_format_character(room) for room in await results.fetchall()]
        return characters

    @classmethod
    async def get_characters_by_owner(cls, member_id: int) -> List[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.owner_id == member_id)
        results = await table.execute(query)
        characters = [_format_character(room) for room in await results.fetchall()]
        return characters

    @classmethod
    async def update_character(cls, character_id: int, **kwargs) -> None:
        if 'updated' not in kwargs:
            kwargs['updated'] = int(time.time())
        query = cls.t.update().values(kwargs).where(cls.t.c.id == character_id)
        await table.execute(query)

    @classmethod
    async def create_character(cls, member_id: int, campaign_id: int, name: str, avatar: str, description: str,
                               data: dict) -> ObjectDict:
        created = int(time.time())
        url_token = base62.encode(get_id())
        values = ObjectDict(
            url_token=url_token,
            member_id=member_id,
            campaign_id=campaign_id,
            name=name,
            avatar=avatar,
            description=description,
            is_removed=0,
            data=data,
            created=created,
            updated=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        character = _format_character(values)
        return character
