#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from typing import Optional, Iterable, Dict, List

import base62
from sqlalchemy import select, and_

from epicteller.core.model.episode import Episode
from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.enum import EpisodeState
from epicteller.core.util.seq import get_id


def _format_episode(result) -> Optional[Episode]:
    if not result:
        return None
    episode = Episode(
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


class EpisodeDAO:
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
    async def batch_get_episode_by_id(cls, episode_ids: Iterable[int]) -> Dict[int, Episode]:
        query = cls.select_clause.where(cls.t.c.id.in_(list(set(episode_ids))))
        result = await table.execute(query)
        rows = await result.fetchall()
        return {row.id: _format_episode(row) for row in rows}

    @classmethod
    async def batch_get_episode_by_url_token(cls, url_tokens: Iterable[str]) -> Dict[str, Episode]:
        query = cls.select_clause.where(cls.t.c.url_token.in_(list(set(url_tokens))))
        result = await table.execute(query)
        rows = await result.fetchall()
        return {row.url_token: _format_episode(row) for row in rows}

    @classmethod
    async def get_episode_ids_by_room_states(cls, room_id: int, states: Iterable[EpisodeState]) -> List[int]:
        query = select([cls.t.c.id]).where(
            and_(cls.t.c.room_id == room_id,
                 cls.t.c.state.in_([int(state) for state in states])),
        )
        result = await table.execute(query)
        rows = await result.fetchall()
        episode_ids = [row.id for row in rows]
        episode_ids.sort()
        return episode_ids

    @classmethod
    async def get_episode_ids_by_campaign(cls, campaign_id: int) -> List[int]:
        query = select([cls.t.c.id]).where(
            cls.t.c.campaign_id == campaign_id,
        )
        result = await table.execute(query)
        rows = await result.fetchall()
        episode_ids = [row.id for row in rows]
        episode_ids.sort()
        return episode_ids

    @classmethod
    async def update_episode(cls, episode_id: int, **kwargs) -> None:
        if len(kwargs) == 0:
            return
        if 'updated' not in kwargs:
            kwargs['updated'] = int(time.time())
        query = cls.t.update().values(kwargs).where(cls.t.c.id == episode_id)
        await table.execute(query)

    @classmethod
    async def create_episode(cls, room_id: int, campaign_id: int, title: str, state: EpisodeState) -> Episode:
        created = int(time.time())
        url_token = base62.encode(get_id())
        values = ObjectDict(
            url_token=url_token,
            room_id=room_id,
            campaign_id=campaign_id,
            title=title,
            state=int(state),
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
