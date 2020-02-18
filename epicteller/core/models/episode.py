#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from typing import List, Optional

import base62
from sqlalchemy import select, and_

from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.const import EpisodeState
from epicteller.core.util.seq import get_id


def _format_episode(result) -> Optional[ObjectDict]:
    if not result:
        return None
    episode = ObjectDict(
        id=result.id,
        url_token=result.url_token,
        room_id=result.room_id,
        campaign_id=result.campaign_id,
        title=result.title,
        state=EpisodeState(result.state),
        is_removed=bool(result.is_removed),
        started_at=result.started_at,
        ended_at=result.ended_at,
        created=result.created,
        updated=result.updated,
    )
    return episode


class Episode:
    t = table.episode

    select_clause = select([
        t.c.id,
        t.c.url_token,
        t.c.room_id,
        t.c.campaign_id,
        t.c.title,
        t.c.state,
        t.c.is_removed,
        t.c.started_at,
        t.c.ended_at,
        t.c.created,
        t.c.updated,
    ])
    
    @classmethod
    async def get_episode_by_id(cls, episode_id: int) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.id == episode_id)
        result = await table.execute(query)
        return _format_episode(await result.fetchone())

    @classmethod
    async def get_episode_by_url_token(cls, url_token: str) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.url_token == url_token)
        result = await table.execute(query)
        return _format_episode(await result.fetchone())

    @classmethod
    async def update_episode(cls, episode_id: int, **kwargs) -> None:
        if 'updated' not in kwargs:
            kwargs['updated'] = int(time.time())
        query = cls.t.update().values(kwargs).where(cls.t.c.id == episode_id)
        await table.execute(query)

    @classmethod
    async def create_episode(cls, room_id: int, campaign_id: int, title: str):
        created = int(time.time())
        url_token = base62.encode(get_id())
        values = ObjectDict(
            url_token=url_token,
            room_id=room_id,
            campaign_id=campaign_id,
            title=title,
            state=int(EpisodeState.RUNNING),
            is_removed=0,
            started_at=created,
            ended_at=None,
            created=created,
            updated=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        episode = _format_episode(values)
        return episode
