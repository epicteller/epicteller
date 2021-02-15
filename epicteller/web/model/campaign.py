#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, List

from pydantic import BaseModel

from epicteller.web.model.character import Character
from epicteller.web.model.episode import Episode
from epicteller.web.model.member import Member


class CampaignRelationship(BaseModel):
    is_gm: bool = False
    is_player: bool = False
    using_character: Optional[Character]


class Campaign(BaseModel):
    id: str
    type: str = 'campaign'
    room_id: str
    name: str
    description: str
    owner: Member
    state: str
    last_episode: Optional[Episode]
    created: int
    updated: int
    characters: Optional[List[Character]]
    relationship: Optional[CampaignRelationship]
