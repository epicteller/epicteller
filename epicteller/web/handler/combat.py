#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from epicteller.core.controller import character as character_ctl
from epicteller.core.controller import combat as combat_ctl
from epicteller.core.model.combat import Combat, CombatToken
from epicteller.core.error.base import NotFoundError
from epicteller.web.fetcher import combat as combat_fetcher
from epicteller.web.model.combat import Combat as WebCombat
from epicteller.web.model.combat import CombatToken as WebCombatToken

router = APIRouter()


async def must_prepare_combat(url_token: str) -> Combat:
    combat = await combat_ctl.get_combat(url_token=url_token)
    if not combat:
        raise NotFoundError()
    return combat


@router.get('/{url_token}', response_model=WebCombat, response_model_exclude_none=True)
async def get_combat(url_token: str):
    combat = await must_prepare_combat(url_token=url_token)
    web_combat = await combat_fetcher.fetch_combat(combat)
    return web_combat


class CombatTokenIn(BaseModel):
    name: str
    initiative: float = 0
    character_id: Optional[str]


@router.post('/{url_token}/tokens', response_model=WebCombatToken, response_model_exclude_none=True)
async def add_combat_token(url_token: str, token_in: CombatTokenIn):
    combat = await must_prepare_combat(url_token)
    character_id: Optional[int] = None
    if token_in.character_id:
        character = await character_ctl.get_character(url_token=token_in.character_id)
        if not character:
            raise NotFoundError()
        character_id = character.id
    token = CombatToken(name=token_in.name, initiative=token_in.initiative, character_id=character_id)
    await combat_ctl.add_combat_token(combat, token)
    web_token = await combat_fetcher.fetch_combat_token(token)
    return web_token
