#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request

from epicteller.core.controller import member as member_ctl
from epicteller.web.model import BasicResponse
from epicteller.web.model.member import MemberSettings, ExternalBindForm

router = APIRouter()


@router.get('/me')
async def me():
    return


@router.post('/me', response_model=BasicResponse)
async def update_profile(request: Request, settings: MemberSettings):
    member_id = request.user.id
    setting_dict = settings.dict()
    await member_ctl.update_member(member_id, **setting_dict)
    return BasicResponse()
