#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel

from epicteller.web.model.member import Member


class Character(BaseModel):
    id: str
    type: str = 'character'
    member: Optional[Member]
    name: str
    avatar: str
    description: str
    is_removed: Optional[bool]
    raw_data: dict
    created: int
    updated: int
