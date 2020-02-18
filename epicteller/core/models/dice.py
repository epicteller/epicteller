#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from typing import List, Optional

import base62
from sqlalchemy import select, and_

from epicteller.core.tables import table
from epicteller.core.util import ObjectDict
from epicteller.core.util.const import DiceType
from epicteller.core.util.seq import get_id


def _format_dice(result) -> Optional[ObjectDict]:
    if not result:
        return None
    dice = ObjectDict(
        id=result.id,
        url_token=result.url_token,
        character_id=result.character_id,
        episode_id=result.episode_id,
        type=DiceType(result.type),
        expression=result.expression,
        detail=result.detail,
        reason=result.reason,
        result=result.result,
        created=result.created,
    )
    return dice


class Dice:
    t = table.dice

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
    async def get_dice_by_id(cls, dice_id: int) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.id == dice_id)
        result = await table.execute(query)
        return _format_dice(await result.fetchone())

    @classmethod
    async def get_dice_by_url_token(cls, url_token: str) -> Optional[ObjectDict]:
        query = cls.select_clause.where(cls.t.c.url_token == url_token)
        result = await table.execute(query)
        return _format_dice(await result.fetchone())

    @classmethod
    async def update_dice(cls, dice_id: int, **kwargs) -> None:
        if 'updated' not in kwargs:
            kwargs['updated'] = int(time.time())
        query = cls.t.update().values(kwargs).where(cls.t.c.id == dice_id)
        await table.execute(query)

    @classmethod
    async def create_dice(cls, character_id: int, episode_id: int, dice_type: DiceType, expression: str,
                          detail: str, reason: str, result: dict) -> ObjectDict:
        created = int(time.time())
        url_token = base62.encode(get_id())
        values = ObjectDict(
            url_token=url_token,
            character_id=character_id,
            episode_id=episode_id,
            type=int(dice_type),
            expression=expression,
            detail=detail,
            reason=reason,
            result=result,
            created=created,
        )
        query = cls.t.insert().values(values)
        result = await table.execute(query)
        values.id = result.lastrowid
        dice = _format_dice(values)
        return dice
