#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
import random
import secrets
from typing import Optional, Iterable, Dict, Union

from datum import Parser
from datum.base import Result

from epicteller.core.config import Config
from epicteller.core.dao.dice import DiceDAO
from epicteller.core.model.dice import Dice
from epicteller.core.util.enum import DiceType
from epicteller.core.util.typing import DiceValue_T

parser = Parser()
rand = random.Random()


def get_rand_obj() -> random.Random:
    return rand


async def roll_dice(expr: str) -> Result:
    component = parser.parse(expr)
    component.set_dice_generator(lambda face: get_rand_obj().randint(1, face))
    result = component.to_result()
    await update_memory_dump()
    return result


async def update_memory_dump():
    data = pickle.dumps(rand)
    await DiceDAO.update_memory_dump(Config.RUNTIME_ID, data)


async def receive_memory_dump(dump: Optional[bytes] = None):
    global rand
    if not dump:
        dump = await DiceDAO.get_memory_dump(Config.RUNTIME_ID)
    if not dump:
        return
    rand = pickle.loads(dump)


async def refresh_randomizer(seed: bytes = None):
    global rand
    if not seed:
        seed = secrets.token_bytes(16)
    rand = random.Random(seed)
    await update_memory_dump()


async def get_dice(dice_id: int=None, *, url_token: str=None) -> Optional[Dice]:
    if dice_id:
        return (await DiceDAO.batch_get_dice_by_id([dice_id])).get(dice_id)
    elif url_token:
        return (await DiceDAO.batch_get_dice_by_url_token([url_token])).get(url_token)
    return None


async def batch_get_dice(dice_ids: Iterable[int]=None, *,
                         url_tokens: Iterable[str]=None) -> Dict[Union[int, str], Dice]:
    if dice_ids:
        return await DiceDAO.batch_get_dice_by_id(dice_ids)
    elif url_tokens:
        return await DiceDAO.batch_get_dice_by_url_token(url_tokens)
    return {}


async def create_dice(character_id: int, episode_id: int, dice_type: DiceType, expression: str,
                      result: Result, reason: str='') -> Dice:
    detail = str(result)
    value: DiceValue_T = result.value
    return await DiceDAO.create_dice(character_id, episode_id, dice_type, expression, detail, value, reason)
