#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel

from epicteller.core.util.enum import CombatState


class Combat(BaseModel):
    id: int
    url_token: str
    room_id: int
    state: CombatState


class CombatToken(BaseModel):
    name: str
    initiative: int
    character_id: Optional[int]

