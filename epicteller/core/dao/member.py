#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
from dataclasses import asdict
from typing import Optional, Dict, Iterable

import base62
from sqlalchemy import select, and_

from epicteller.core import redis
from epicteller.core.config import Config
from epicteller.core.model.member import Member, Credential
from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.enum import ExternalType
from epicteller.core.util.seq import get_id


def _format_member(result) -> Optional[Member]:
    if not result:
        return None
    member = Member(
        id=result.id,
        url_token=result.url_token,
        name=result.name,
        email=result.email,
        passhash=result.passhash,
        headline=result.headline,
        avatar=result.avatar,
        created=result.created,
    )
    return member


class MemberDAO:
    t = table.member
    r = redis.redis
    select_clause = select([
        t.c.id,
        t.c.url_token,
        t.c.name,
        t.c.email,
        t.c.passhash,
        t.c.headline,
        t.c.avatar,
        t.c.created,
    ])

    @classmethod
    async def batch_get_member_by_id(cls, member_ids: Iterable[int]) -> Dict[int, Member]:
        query = cls.select_clause.where(cls.t.c.id.in_(member_ids))
        result = await table.execute(query)
        rows = await result.fetchall()
        members = {row.id: _format_member(row) for row in rows}
        return members

    @classmethod
    async def batch_get_member_by_url_token(cls, url_tokens: Iterable[str]) -> Dict[str, Member]:
        query = cls.select_clause.where(cls.t.c.url_token.in_(url_tokens))
        result = await table.execute(query)
        rows = await result.fetchall()
        members = {row.url_token: _format_member(row) for row in rows}
        return members

    @classmethod
    async def get_member_by_email(cls, email: str) -> Optional[Member]:
        query = cls.select_clause.where(cls.t.c.email == email)
        result = await table.execute(query)
        return _format_member(await result.fetchone())

    @classmethod
    async def get_member_by_external_id(cls, external_id: str) -> Optional[Member]:
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
                            headline: str='', avatar: str='') -> Member:
        created = int(time.time())
        url_token = base62.encode(get_id())
        values = ObjectDict(
            url_token=url_token,
            name=name,
            email=email,
            passhash=passhash,
            headline=headline,
            avatar=avatar,
            created=created,
            updated=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        member = _format_member(values)
        return member

    @classmethod
    async def create_access_token(cls, member_id: int, token: str):
        ttl = Config.ACCESS_TOKEN_TTL
        now = int(time.time())
        expired_at = now + ttl
        data = Credential(member_id=member_id, token=token, created_at=now, expired_at=expired_at).to_json()
        await cls.r.set(f'access_token:{token}', data, expire=ttl)

    @classmethod
    async def create_refresh_token(cls, member_id: int, token: str):
        await cls.r.set(f'access_token:{token}', data, expire=ttl)

    @classmethod
    async def revoke_access_token(cls, token: str):
        await cls.r.expire(f'access_token:{token}', 10)

    @classmethod
    async def revoke_refresh_token(cls, token: str):
        await cls.r.expire(f'refresh_token:{token}', 10)

    @classmethod
    async def get_access_token(cls, token: str) -> Optional[Credential]:
        data = await cls.r.get(f'access_token:{token}')
        if not data:
            return
        return Credential.from_json(data)

    @classmethod
    async def get_refresh_token(cls, token: str) -> Optional[Credential]:
        data = await cls.r.get(f'refresh_token:{token}')
        if not data:
            return
        return Credential.from_json(data)


class MemberExternalDAO:
    t = table.member_external_id

    @classmethod
    async def get_member_id_by_external(cls, external_type: ExternalType, external_id: str) -> Optional[int]:
        query = select([cls.t.c.member_id]).where(and_(cls.t.c.type == int(external_type),
                                                       cls.t.c.external_id == external_id))
        result = await table.execute(query)
        member_id = await result.scalar()
        return member_id

    @classmethod
    async def get_external_ids_by_member(cls, member_id: int) -> Dict[ExternalType, str]:
        query = select([
            cls.t.c.type,
            cls.t.c.external_id,
        ]).where(cls.t.c.member_id == member_id)
        result = await table.execute(query)
        rows = await result.fetchall()
        externals = {ExternalType(row.type): row.external_id for row in rows}
        return externals

    @classmethod
    async def bind_member_external_id(cls, member_id: int, external_type: ExternalType, external_id: str) -> None:
        query = cls.t.insert().values(
            member_id=member_id,
            type=int(external_type),
            external_id=external_id,
        )
        await table.execute(query)

    @classmethod
    async def unbind_member_external_id(cls, member_id: int, external_type: ExternalType) -> None:
        query = cls.t.delete().where(and_(cls.t.c.member_id == member_id, cls.t.c.type == int(external_type)))
        await table.execute(query)
