#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from typing import Optional, Iterable, Dict, List

import base62
from sqlalchemy import select, and_, func

from epicteller.core.model.campaign import Campaign
from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.enum import CampaignState
from epicteller.core.util.seq import get_id


def _format_campaign(result) -> Optional[Campaign]:
    if not result:
        return
    campaign = Campaign(
        id=result.id,
        url_token=result.url_token,
        room_id=result.room_id,
        name=result.name,
        description=result.description,
        owner_id=result.owner_id,
        state=CampaignState(result.state),
        is_removed=bool(result.is_removed),
        last_episode_id=result.last_episode_id or None,
        created=result.created,
        updated=result.updated,
    )
    return campaign


class CampaignDAO:
    t = table.campaign

    select_clause = select([
        t.c.id,
        t.c.url_token,
        t.c.room_id,
        t.c.name,
        t.c.description,
        t.c.owner_id,
        t.c.state,
        t.c.is_removed,
        t.c.last_episode_id,
        t.c.created,
        t.c.updated,
    ])
    
    @classmethod
    async def batch_get_campaign_by_id(cls, campaign_ids: Iterable[int]) -> Dict[int, Campaign]:
        query = cls.select_clause.where(cls.t.c.id.in_(campaign_ids))
        result = await table.execute(query)
        rows = await result.fetchall()
        return {row.id: _format_campaign(row) for row in rows}

    @classmethod
    async def batch_get_campaign_by_url_token(cls, url_tokens: Iterable[str]) -> Dict[str, Campaign]:
        query = cls.select_clause.where(cls.t.c.url_token.in_(url_tokens))
        result = await table.execute(query)
        rows = await result.fetchall()
        return {row.url_token: _format_campaign(row) for row in rows}

    @classmethod
    async def get_campaign_ids_by_room(cls, room_id: int, after: int = 0, limit: int = 20) -> List[int]:
        query = select([cls.t.c.id]).where(and_(
            cls.t.c.room_id == room_id,
            cls.t.c.id > after,
        )).limit(limit)
        result = await table.execute(query)
        rows = await result.fetchall()
        return [row.id for row in rows]

    @classmethod
    async def get_campaign_ids_by_owner(cls, member_id: int) -> List[int]:
        query = select([cls.t.c.id]).where(cls.t.c.owner_id == member_id)
        result = await table.execute(query)
        rows = await result.fetchall()
        return [row.id for row in rows]

    @classmethod
    async def batch_get_campaign_count_by_room(cls, room_ids: List[int]) -> Dict[int, int]:
        query = select([cls.t.c.room_id,
                        func.count(cls.t.c.id).label('c')]
                       ).where(cls.t.c.room_id.in_(room_ids)).group_by(cls.t.c.room_id)
        result = await table.execute(query)
        rows = await result.fetchall()
        count_map = {rid: 0 for rid in room_ids}
        for r in rows:
            count_map[r.room_id] = r.c
        return count_map

    @classmethod
    async def update_campaign(cls, campaign_id: int, **kwargs) -> None:
        if 'updated' not in kwargs:
            kwargs['updated'] = int(time.time())
        query = cls.t.update().values(kwargs).where(cls.t.c.id == campaign_id)
        await table.execute(query)

    @classmethod
    async def create_campaign(cls, room_id: int, name: str, description: str, owner_id: int) -> Campaign:
        created = int(time.time())
        url_token = base62.encode(get_id())
        values = ObjectDict(
            url_token=url_token,
            room_id=room_id,
            name=name,
            description=description,
            owner_id=owner_id,
            state=int(CampaignState.PREPARING),
            is_removed=0,
            last_episode_id=0,
            created=created,
            updated=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        campaign = _format_campaign(values)
        return campaign
