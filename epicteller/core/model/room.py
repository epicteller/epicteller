#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel


class Room(BaseModel):
    id: int
    url_token: str
    name: str
    description: str
    is_removed: bool
    current_campaign_id: Optional[int]
    avatar: str
    created: int
    updated: int
