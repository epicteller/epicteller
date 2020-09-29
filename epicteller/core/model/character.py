#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class Character:
    id: int
    url_token: str
    member_id: int
    campaign_id: int
    name: str
    avatar: str
    description: str
    is_removed: bool
    raw_data: dict
    created: int
    updated: int
