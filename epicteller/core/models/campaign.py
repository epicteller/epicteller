#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from typing import List, Optional

import base62
from sqlalchemy import select, and_

from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.const import CampaignState
from epicteller.core.util.seq import get_id


def _format_campaign(result) -> Optional[ObjectDict]:
    if not result:
        return
    campaign = ObjectDict(
        id=result.id,
        url_token=result.url_token,
        room_id=result.room_id,
        name=result.name,
        description=result.description,
        owner_id=result.owner_id,
        state=CampaignState(result.state),
        is_removed=bool(result.is_removed),
        created=result.created,
        updated=result.updated,
    )
    return campaign


class Campaign:
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
        t.c.created,
        t.c.updated,
    ])
    
    @classmethod
    async def get_campaign_by_id(cls, campaign_id: int) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.id == campaign_id)
        result = await table.execute(query)
        return _format_campaign(await result.fetchone())

    @classmethod
    async def get_campaign_by_url_token(cls, url_token: str) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.url_token == url_token)
        result = await table.execute(query)
        return _format_campaign(await result.fetchone())

    @classmethod
    async def update_campaign(cls, campaign_id: int, **kwargs) -> None:
        if 'updated' not in kwargs:
            kwargs['updated'] = int(time.time())
        query = cls.t.update().values(kwargs).where(cls.t.c.id == campaign_id)
        await table.execute(query)

    @classmethod
    async def create_campaign(cls, room_id: int, name: str, description: str, owner_id: int) -> ObjectDict:
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
            created=created,
            updated=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        campaign = _format_campaign(values)
        return campaign
