#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel, Field

from epicteller.core.util.enum import ExternalType


class MemberSettings(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=20)
    headline: Optional[str] = Field(None, max_length=200)


class ExternalBindForm(BaseModel):
    type: ExternalType = ExternalType.QQ
    external_id: str
    validate_token: str
