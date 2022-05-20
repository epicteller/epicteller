#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from operator import and_
from typing import Iterable, Dict, Optional, List

import base62
from sqlalchemy import select

from epicteller.core.model.combat import Combat, CombatToken, CombatOrder
from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.enum import CombatState
from epicteller.core.util.seq import get_id


def _format_combat(result) -> Optional[Combat]:
    if not result:
        return

    combat = Combat(
        id=result.id,
        url_token=result.url_token,
        room_id=result.room_id,
        campaign_id=result.campaign_id,
        state=CombatState(result.state),
        is_removed=bool(result.is_removed),
        tokens={name: CombatToken.parse_obj(token) for name, token in result.tokens.items()},
        order=CombatOrder.parse_obj(result.order),
        data=result.data,
        started_at=result.started_at,
        ended_at=getattr(result, 'ended_at', None),
        created=result.created,
        updated=result.updated,
    )
    return combat


class CombatDAO:
    t = table.combat

    select_clause = select([
        t.c.id,
        t.c.url_token,
        t.c.room_id,
        t.c.campaign_id,
        t.c.state,
        t.c.is_removed,
        t.c.tokens,
        t.c.order,
        t.c.data,
        t.c.started_at,
        t.c.ended_at,
        t.c.created,
        t.c.updated,
    ])

    @classmethod
    async def batch_get_combat_by_id(cls, combat_ids: Iterable[int]) -> Dict[int, Combat]:
        query = cls.select_clause.where(cls.t.c.id.in_(list(set(combat_ids))))
        result = await table.execute(query)
        rows = await result.fetchall()
        return {row.id: _format_combat(row) for row in rows}

    @classmethod
    async def batch_get_combat_by_url_token(cls, url_tokens: Iterable[str]) -> Dict[str, Combat]:
        query = cls.select_clause.where(cls.t.c.url_token.in_(list(set(url_tokens))))
        result = await table.execute(query)
        rows = await result.fetchall()
        return {row.url_token: _format_combat(row) for row in rows}

    @classmethod
    async def get_combat_ids_by_campaign(cls, campaign_id: int) -> List[int]:
        query = select([cls.t.c.id]).where(
            and_(
                cls.t.c.campaign_id == campaign_id,
                cls.t.c.is_removed == 0,
            ),
        ).order_by(cls.t.c.id)
        results = await table.execute(query)
        rows = await results.fetchall()
        return [row.id for row in rows]

    @classmethod
    async def update_combat(cls, combat_id: int, **kwargs) -> None:
        if len(kwargs) == 0:
            return
        if 'updated' not in kwargs:
            kwargs['updated'] = int(time.time())
        query = cls.t.update().values(kwargs).where(cls.t.c.id == combat_id)
        await table.execute(query)

    @classmethod
    async def create_combat(cls, room_id: int, campaign_id: int) -> Combat:
        created = int(time.time())
        url_token = base62.encode(get_id())
        values = ObjectDict(
            url_token=url_token,
            room_id=room_id,
            campaign_id=campaign_id,
            state=int(CombatState.INITIATING),
            is_removed=0,
            tokens={},
            order={},
            data={},
            started_at=created,
            created=created,
            updated=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        combat = _format_combat(values)
        return combat


class RoomRunningCombatDAO:
    t = table.room_running_combat

    @classmethod
    async def get_running_combat_id(cls, room_id: int) -> Optional[int]:
        query = select([cls.t.c.combat_id]).where(cls.t.c.room_id == room_id)
        result = await table.execute(query)
        return await result.scalar()

    @classmethod
    async def set_running_combat(cls, room_id: int, combat_id: int) -> None:
        result = await cls.get_running_combat_id(room_id)
        if result:
            return
        query = cls.t.insert().values(room_id=room_id, combat_id=combat_id)
        await table.execute(query)

    @classmethod
    async def remove_running_combat(cls, room_id: int) -> None:
        query = cls.t.delete().where(cls.t.c.room_id == room_id)
        await table.execute(query)
