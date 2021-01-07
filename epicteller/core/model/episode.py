#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel

from epicteller.core.util.enum import EpisodeState


class Episode(BaseModel):
    id: int
    url_token: str
    room_id: int
    campaign_id: int
    title: str
    state: EpisodeState
    is_removed: bool
    started_at: int
    ended_at: Optional[int]
    created: int
    updated: int
