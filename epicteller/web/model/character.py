#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel


class Character(BaseModel):
    id: str
    member: Optional[int]  # 暂时先不填充这个了
    name: str
    avatar: str
    description: str
    is_removed: Optional[bool]
    raw_data: dict
    created: int
    updated: int
