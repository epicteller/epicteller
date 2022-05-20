#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Dict, List

from pydantic import BaseModel

from epicteller.core.util.enum import CombatState


class CombatToken(BaseModel):
    name: str
    initiative: float
    character_id: Optional[int]


class CombatOrder(BaseModel):
    order_list: List[str] = []
    current_token_name: Optional[str]
    round_count: int = 0


class Combat(BaseModel):
    id: int
    url_token: str
    room_id: int
    campaign_id: int
    state: CombatState
    is_removed: bool
    tokens: Dict[str, CombatToken]
    order: CombatOrder
    data: dict
    started_at: int
    ended_at: Optional[int]
    created: int
    updated: int
