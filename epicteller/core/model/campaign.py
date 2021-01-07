#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel

from epicteller.core.util.enum import CampaignState


class Campaign(BaseModel):
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
