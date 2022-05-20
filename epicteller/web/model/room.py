#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel

from epicteller.web.model.member import Member


class Room(BaseModel):
    id: str
    type: str = 'room'
    name: str
    description: str
    owner: Member
    is_removed: Optional[bool]
    avatar: str
    created: int
    updated: int
    member_count: Optional[int]
    has_running_campaign: bool
