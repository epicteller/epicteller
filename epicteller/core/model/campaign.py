#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional

from epicteller.core.util.enum import CampaignState


@dataclass
class Campaign:
    id: int
    url_token: str
    room_id: int
    name: str
    description: str
    owner_id: int
    state: CampaignState
    is_removed: bool
    last_episode_id: Optional[int]
    created: int
    updated: int
