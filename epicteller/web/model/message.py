#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Union

from pydantic import BaseModel

from epicteller.web.model.character import Character


class MessageRelationship(BaseModel):
    is_owner: Optional[bool]


class Message(BaseModel):
    id: str
    type: str = 'message'
    campaign_id: str
    episode_id: str
    character: Optional[Character]
    is_removed: Optional[bool]
    is_gm: bool
    message_type: str
    content: dict
    created: int
    updated: int
    relationship: Optional[MessageRelationship]
