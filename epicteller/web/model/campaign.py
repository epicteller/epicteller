#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel

from epicteller.web.model.episode import Episode
from epicteller.web.model.member import Member


class Campaign(BaseModel):
    id: str
    room_id: str
    name: str
    description: str
    owner: Member
    state: str
    last_episode: Optional[Episode]
    created: int
    updated: int
