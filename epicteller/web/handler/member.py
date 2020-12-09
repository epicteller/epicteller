#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends

from epicteller.core.model.member import Member
from epicteller.core.controller import credential as credential_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.web.controller.auth import get_current_member
from epicteller.web.error.auth import EMailValidateError, EMailUsedError
from epicteller.web.model import BasicResponse
from epicteller.web.model.member import MemberSettings, ExternalBindForm

router = APIRouter()


@router.get('/me')
async def me(member: Member = Depends(get_current_member)):
    return member


@router.post('/me', response_model=BasicResponse)
async def update_profile(settings: MemberSettings, member: Member = Depends(get_current_member)):
    setting_dict = settings.dict()
    await member_ctl.update_member(member.id, **setting_dict)
    return BasicResponse()


@router.post('/bind-external', response_model=BasicResponse)
async def bind_external(form: ExternalBindForm, member: Member = Depends(get_current_member)):
    external_id = await member_ctl.get_member_by_external(form.type, form.external_id)
    if external_id:
        raise EMailUsedError()
    expected_email = f'{form.external_id}@qq.com'
    email = await credential_ctl.get_email_validate_token(form.validate_token)
    if email != expected_email:
        raise EMailValidateError()
    await member_ctl.bind_member_external_id(member.id, form.type, form.external_id)
    return BasicResponse()
