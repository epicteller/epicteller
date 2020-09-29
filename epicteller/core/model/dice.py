#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional

from epicteller.core.util.enum import DiceType
from epicteller.core.util.typing import DiceValue_T


@dataclass
class Dice:
    id: int
    url_token: str
    character_id: int
    episode_id: int
    type: DiceType
    expression: str
    detail: str
    reason: Optional[str]
    result: DiceValue_T
    created: int
