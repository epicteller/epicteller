#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from typing import Optional

import base62
from sqlalchemy import select

from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.seq import get_id


def _format_member(result) -> Optional[ObjectDict]:
    if not result:
        return None
    member = ObjectDict(
        id=result.id,
        url_token=result.url_token,
        name=result.name,
        email=result.email,
        passhash=result.passhash,
        headline=result.headline,
        external_id=result.external_id,
        avatar=result.avatar,
        created=result.created,
    )
    return member


class Member:
    t = table.member
    select_clause = select([
        t.c.id,
        t.c.url_token,
        t.c.name,
        t.c.email,
        t.c.passhash,
        t.c.headline,
        t.c.external_id,
        t.c.avatar,
        t.c.created,
    ])

    @classmethod
    async def get_member_by_id(cls, member_id: int) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.id == member_id)
        result = await table.execute(query)
        return _format_member(await result.fetchone())

    @classmethod
    async def get_member_by_url_token(cls, url_token: str) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.url_token == url_token)
        result = await table.execute(query)
        return _format_member(await result.fetchone())

    @classmethod
    async def get_member_by_email(cls, email: str) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.email == email)
        result = await table.execute(query)
        return _format_member(await result.fetchone())

    @classmethod
    async def get_member_by_external_id(cls, external_id: str) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.external_id == external_id)
        result = await table.execute(query)
        return _format_member(await result.fetchone())

    @classmethod
    async def update_member(cls, member_id: int, **kwargs) -> None:
        if 'updated' not in kwargs:
            kwargs['updated'] = int(time.time())
        query = cls.t.update().values(kwargs).where(cls.t.c.id == member_id)
        await table.execute(query)

    @classmethod
    async def create_member(cls, name: str, email: str, passhash: str,
                            headline: str='', external_id: str='', avatar: str='') -> Optional[ObjectDict]:
        created = int(time.time())
        url_token = base62.encode(get_id())
        values = ObjectDict(
            url_token=url_token,
            name=name,
            email=email,
            passhash=passhash,
            headline=headline,
            external_id=external_id,
            avatar=avatar,
            created=created,
            updated=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        member = _format_member(values)
        return member
