#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Member(BaseModel):
    id: int
    url_token: str
    name: str
    email: str
    passhash: str
    headline: str
    avatar: str
    created: int
