#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel


class Episode(BaseModel):
    id: str
    type: str = 'episode'
    room_id: str
    campaign_id: str
    title: str
    state: str
    started_at: int
    ended_at: Optional[int]
    created: int
    updated: int
