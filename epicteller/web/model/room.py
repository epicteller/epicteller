#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel


class Room(BaseModel):
    id: str
    name: str
    description: str
    is_removed: Optional[bool]
    avatar: str
    created: int
    updated: int
