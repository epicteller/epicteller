#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel

from epicteller.core.util.enum import ExternalType


class Room(BaseModel):
    id: int
    url_token: str
    name: str
    description: str
    owner_id: int
    is_removed: bool
    current_campaign_id: Optional[int]
    avatar: str
    created: int
    updated: int


class RoomExternalInfo(BaseModel):
    room_id: int
    type: ExternalType
    external_id: str
    bot_id: str
