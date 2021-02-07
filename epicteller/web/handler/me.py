#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Request
from starlette.authentication import requires

from epicteller.core.controller import member as member_ctl
from epicteller.web.error.auth import UnauthorizedError
from epicteller.web.fetcher.member import fetch_me
from epicteller.web.model import BasicResponse
from epicteller.web.model.member import MeSettings, Me

router = APIRouter()


@requires(['login'], 401)
@router.get('', response_model=Me, response_model_exclude_none=True)
async def me(request: Request):
    if not request.user:
        raise UnauthorizedError()
    member_id = request.user.id
    member = await member_ctl.get_member(member_id)
    return await fetch_me(member)


@router.put('', response_model=BasicResponse)
@requires(['login'], 401)
async def update_profile(request: Request, settings: MeSettings):
    member_id = request.user.id
    setting_dict = settings.dict(exclude_unset=True)
    await member_ctl.update_member(member_id, **setting_dict)
    return BasicResponse()
