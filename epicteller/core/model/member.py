#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class Member:
    id: int
    url_token: str
    name: str
    email: str
    passhash: str
    headline: str
    avatar: str
    created: int
