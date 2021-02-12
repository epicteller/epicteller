#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel

from epicteller.core.model.message import MessageContent
from epicteller.web.model.character import Character


class Message(BaseModel):
    id: str
    episode_id: str
    character: Optional[Character]
    is_removed: Optional[bool]
    is_gm: bool
    type: str
    content: MessageContent
    created: int
    updated: int
