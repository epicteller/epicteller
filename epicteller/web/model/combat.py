#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict, Optional, List

from pydantic import BaseModel

from epicteller.web.model.character import Character
from epicteller.web.model.room import Room


class CombatToken(BaseModel):
    name: str
    initiative: float
    character: Optional[Character]


class CombatOrder(BaseModel):
    order: List[CombatToken]
    current_token: Optional[CombatToken]
    round_count: int = 0


class Combat(BaseModel):
    id: str
    type: str = 'combat'
    room: Room
    campaign_id: Optional[str]
    state: str
    is_removed: bool
    tokens: Dict[str, CombatToken]
    order: CombatOrder
    data: dict
    started_at: int
    ended_at: Optional[int]
    created: int
    updated: int
