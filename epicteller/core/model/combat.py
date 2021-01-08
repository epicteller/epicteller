#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Dict

from pydantic import BaseModel

from epicteller.core.util.enum import CombatState


class CombatToken(BaseModel):
    name: str
    initiative: int
    character_id: Optional[int]


class Combat(BaseModel):
    id: int
    url_token: str
    room_id: int
    state: CombatState
    tokens_map: Dict[str, CombatToken]

