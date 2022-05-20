#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from starlette.requests import Request

from epicteller.core.error.base import NotFoundError
from epicteller.core.model.character import Character
from epicteller.core.controller import character as character_ctl
from epicteller.web.error.permission import PermissionDeniedError
from epicteller.web.middleware.auth import requires
from epicteller.web.model import BasicResponse
from epicteller.web.model.character import Character as WebCharacter, UpdateCharacter
from epicteller.web.fetcher import character as character_fetcher

router = APIRouter()


async def prepare(url_token: str) -> Character:
    character = await character_ctl.get_character(url_token=url_token)
    if not character:
        raise NotFoundError()
    return character


@router.get('/characters/{url_token}', response_model=WebCharacter, response_model_exclude_none=True)
async def get_character(r: Request, character: Character = Depends(prepare)):
    web_character = await character_fetcher.fetch_character(character, r.user.id)
    return web_character


@router.put('/characters/{url_token}', response_model=BasicResponse, response_model_exclude_none=True)
@requires(['login'])
async def update_character(r: Request, update: UpdateCharacter,
                           character: Character = Depends(prepare)):
    member_id = r.user.id
    if character.member_id != member_id:
        raise PermissionDeniedError()
    update_dict = update.dict(exclude_unset=True)
    await character_ctl.update_character(character, **update_dict)
    return BasicResponse()
