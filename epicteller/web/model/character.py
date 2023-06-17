#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel, Field

from epicteller.web.model.member import Member


class CharacterRelationship(BaseModel):
    is_owner: bool = False


class Character(BaseModel):
    id: str
    type: str = 'character'
    member: Optional[Member]
    name: str
    avatar: str
    avatar_template: str
    description: str
    is_removed: Optional[bool]
    raw_data: dict
    created: int
    updated: int
    relationship: Optional[CharacterRelationship]


class UpdateCharacter(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=20)
    avatar: Optional[str] = Field(None, regex=r'^v1-[0-9a-f]{32}$')
    description: Optional[str] = Field(None, max_length=65535)
