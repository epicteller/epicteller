#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
from typing import Optional, Iterable, Dict

import base62
from sqlalchemy import select

from epicteller.core import redis
from epicteller.core.model.dice import Dice
from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.enum import DiceType
from epicteller.core.util.seq import get_id
from epicteller.core.util.typing import DiceValue_T


def _format_dice(result) -> Optional[Dice]:
    if not result:
        return None
    dice = Dice(
        id=result.id,
        url_token=result.url_token,
        character_id=result.character_id,
        episode_id=result.episode_id,
        type=DiceType(result.type),
        expression=result.expression,
        detail=result.detail,
        reason=result.reason or None,
        result=result.result,
        created=result.created,
    )
    return dice


class DiceDAO:
    t = table.dice
    r = redis.redis

    select_clause = select([
        t.c.id,
        t.c.url_token,
        t.c.character_id,
        t.c.episode_id,
        t.c.type,
        t.c.expression,
        t.c.detail,
        t.c.reason,
        t.c.result,
        t.c.created,
    ])
    
    @classmethod
    async def batch_get_dice_by_id(cls, dice_ids: Iterable[int]) -> Dict[int, Dice]:
        query = cls.select_clause.where(cls.t.c.id.in_(dice_ids))
        res = await table.execute(query)
        rows = res.fetchall()
        return {row.id: _format_dice(row) for row in rows}

    @classmethod
    async def batch_get_dice_by_url_token(cls, url_tokens: Iterable[str]) -> Dict[str, Dice]:
        query = cls.select_clause.where(cls.t.c.url_token.in_(url_tokens))
        res = await table.execute(query)
        rows = res.fetchall()
        return {row.url_token: _format_dice(row) for row in rows}

    @classmethod
    async def update_dice(cls, dice_id: int, **kwargs) -> None:
        query = cls.t.update().values(kwargs).where(cls.t.c.id == dice_id)
        await table.execute(query)

    @classmethod
    async def create_dice(cls, character_id: int, episode_id: int, dice_type: DiceType, expression: str,
                          detail: str, result: DiceValue_T, reason: Optional[str]= '') -> Dice:
        created = int(time.time())
        url_token = base62.encode(get_id())
        values = ObjectDict(
            url_token=url_token,
            character_id=character_id,
            episode_id=episode_id,
            type=int(dice_type),
            expression=expression,
            detail=detail,
            reason=reason if reason else '',
            result=result,
            created=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        dice = _format_dice(values)
        return dice

    @classmethod
    async def update_memory_dump(cls, runtime_id: str, data: bytes):
        await cls.r.set(f'memory_dump:{runtime_id}', data, expire=86400)
