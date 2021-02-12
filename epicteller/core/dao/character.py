#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from collections import defaultdict
from typing import List, Optional, Iterable, Dict

import base62
from sqlalchemy import select, and_
from sqlalchemy.dialects.mysql import insert as mysql_insert

from epicteller.core.model.character import Character
from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.enum import ExternalType
from epicteller.core.util.seq import get_id


def _format_character(result) -> Optional[Character]:
    if not result:
        return
    character = Character(
        id=result.id,
        url_token=result.url_token,
        member_id=result.member_id,
        name=result.name,
        avatar=result.avatar,
        description=result.description,
        is_removed=bool(result.is_removed),
        raw_data=result.data,
        created=result.created,
        updated=result.updated,
    )
    return character


class CharacterDAO:
    t = table.character
    select_clause = select([
        t.c.id,
        t.c.url_token,
        t.c.name,
        t.c.member_id,
        t.c.avatar,
        t.c.description,
        t.c.is_removed,
        t.c.data,
        t.c.created,
        t.c.updated,
    ])

    @classmethod
    async def batch_get_character_by_id(cls, character_ids: Iterable[int]) -> Dict[int, Character]:
        query = cls.select_clause.where(cls.t.c.id.in_(character_ids))
        result = await table.execute(query)
        rows = await result.fetchall()
        return {row.id: _format_character(row) for row in rows}

    @classmethod
    async def batch_get_character_by_url_token(cls, url_tokens: Iterable[str]) -> Dict[str, Character]:
        query = cls.select_clause.where(cls.t.c.url_token.in_(url_tokens))
        result = await table.execute(query)
        rows = await result.fetchall()
        return {row.url_token: _format_character(result) for row in rows}

    @classmethod
    async def get_characters_by_owner(cls, member_id: int) -> List[Character]:
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
    async def create_character(cls, member_id: int, name: str, avatar: str, description: str,
                               raw_data: dict) -> Character:
        created = int(time.time())
        url_token = base62.encode(get_id())
        values = ObjectDict(
            url_token=url_token,
            member_id=member_id,
            name=name,
            avatar=avatar,
            description=description,
            is_removed=0,
            data=raw_data,
            created=created,
            updated=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        character = _format_character(values)
        return character


class CharacterCampaignDAO:
    t = table.character_campaign_index

    @classmethod
    async def get_character_id_by_campaign_name(cls, campaign_id: int, name: str) -> Optional[int]:
        query = select([cls.t.c.character_id]).where(and_(cls.t.c.campaign_id == campaign_id,
                                                          cls.t.c.name == name))
        result = await table.execute(query)
        row = await result.fetchone()
        if not row:
            return
        return int(row.character_id)

    @classmethod
    async def get_character_ids_by_campaign_id(cls, campaign_id: int) -> List[int]:
        query = select([cls.t.c.character_id]).where(cls.t.c.campaign_id == campaign_id)
        results = await table.execute(query)
        character_ids = [int(row.character_id) for row in await results.fetchall()]
        return character_ids

    @classmethod
    async def get_campaign_ids_by_character_ids(cls, character_ids: List[int]) -> Dict[int, List[int]]:
        query = select([
            cls.t.c.character_id,
            cls.t.c.campaign_id,
        ]).where(cls.t.c.character_id.in_(character_ids))
        results = await table.execute(query)
        rows = await results.fetchall()
        campaign_map = defaultdict(list)
        for r in rows:
            campaign_map[r.character_id].append(r.campaign_id)
        return dict(campaign_map)

    @classmethod
    async def bind_character_to_campaign(cls, character_id: int, name: str, campaign_id: int):
        query = mysql_insert(cls.t).values(
            character_id=character_id,
            name=name,
            campaign_id=campaign_id,
        ).on_duplicate_key_update(
            name=name,
        )
        await table.execute(query)

    @classmethod
    async def unbind_character_to_campaign(cls, character_id: int, campaign_id: int):
        query = cls.t.delete().where(and_(cls.t.c.character_id == character_id, cls.t.c.campaign_id == campaign_id))
        await table.execute(query)


class CharacterExternalDAO:
    t = table.character_external_id

    @classmethod
    async def get_external_ids_by_character(cls, character_id: int) -> Dict[ExternalType, str]:
        query = select([
            cls.t.c.type,
            cls.t.c.external_id,
        ]).where(cls.t.c.character_id == character_id)
        result = await table.execute(query)
        rows = await result.fetchall()
        externals = {ExternalType(row.type): row.external_id for row in rows}
        return externals

    @classmethod
    async def bind_character_external_id(cls, character_id: int, external_type: ExternalType, external_id: str):
        query = mysql_insert(cls.t).values(
            character_id=character_id,
            type=int(external_type),
            external_id=external_id,
        ).on_duplicate_key_update(
            external_id=external_id,
        )
        await table.execute(query)

    @classmethod
    async def unbind_character_external_id(cls, character_id: int, external_type: ExternalType):
        query = cls.t.delete().where(and_(cls.t.c.character_id == character_id, cls.t.c.type == int(external_type)))
        await table.execute(query)
