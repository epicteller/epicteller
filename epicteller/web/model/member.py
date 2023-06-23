#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel, Field

from epicteller.core.util.enum import ExternalType


class MeSettings(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=20)
    headline: Optional[str] = Field(None, max_length=200)
    avatar: Optional[str] = Field(None, regex=r'^v1-[0-9a-f]{32}$')


class ExternalBindForm(BaseModel):
    type: ExternalType = ExternalType.QQ
    external_id: str
    validate_token: str


class MemberExternalInfo(BaseModel):
    QQ: Optional[str]


class Member(BaseModel):
    id: str
    type: str = 'member'
    name: str
    headline: str
    avatar: str
    avatar_template: Optional[str]
    created: int


class Me(Member):
    email: str
    avatar_original: str
    external_info: MemberExternalInfo
