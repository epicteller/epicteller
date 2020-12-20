#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from epicteller.core.util.enum import CombatState


@dataclass
class Combat:
    id: int
    url_token: str
    campaign_id: int
    state: CombatState
