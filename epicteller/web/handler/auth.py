#!/usr/bin/env python
# -*- coding: utf-8 -*-
import secrets
from enum import Enum
from typing import Optional

from fastapi import APIRouter, Body, Request, BackgroundTasks, Response, Query
from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr
from starlette.authentication import requires

from epicteller.core.controller import credential as credential_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.core.util.enum import ExternalType
from epicteller.web import worker
from epicteller.web.error import auth as auth_error
from epicteller.web.controller import auth as auth_web_ctl
from epicteller.web.middleware.auth import User
from epicteller.web.model import BasicResponse

router = APIRouter()


class RegisterInfo(BaseModel):
    email: str


@router.get('/register', response_model=RegisterInfo)
async def register_info(token: str = Query(...)):
    email = await credential_ctl.get_email_validate_token('register', token)
    if not email:
        raise auth_error.InvalidValidateTokenError()
    return RegisterInfo(email=email)


class RegisterForm(BaseModel):
    validate_token: str
    password: str = Field(min_length=10, max_length=50)
    name: str


@router.post('/register', response_model=BasicResponse)
async def register(form: RegisterForm, r: Response):
    email = await credential_ctl.get_email_validate_token('register', form.validate_token)
    if not email:
        raise auth_error.InvalidValidateTokenError()
    member = await member_ctl.get_member(email=email)
    if member:
        raise auth_error.EMailUsedError()
    member = await member_ctl.create_member(name=form.name,
                                            email=email,
                                            password=form.password)
    await auth_web_ctl.create_credential(r, member.id)
    return BasicResponse()


class LoginForm(BaseModel):
    email: EmailStr
    password: str


@router.post('/login', response_model=BasicResponse)
async def login(login_form: LoginForm, r: Response):
    email = login_form.email
    password = login_form.password
    member = await member_ctl.check_member_email_password(email, password)
    if not member:
        return auth_error.IncorrectEMailPasswordError()
    await auth_web_ctl.create_credential(r, member.id)
    return BasicResponse()


@router.post('/logout', response_model=BasicResponse)
async def logout(req: Request, resp: Response):
    if not req.user:
        return BasicResponse()
    user: User = req.user
    await credential_ctl.revoke_access_credential(user.access_token)
    await auth_web_ctl.revoke_credential(resp)
    return BasicResponse()


class EmailValidateForm(BaseModel):
    email: EmailStr


@router.post('/validate/register', response_model=BasicResponse)
async def email_validate(tasks: BackgroundTasks, form: EmailValidateForm):
    email = form.email
    member = await member_ctl.get_member(email=email)
    if member:
        raise auth_error.EMailUsedError()
    token = await credential_ctl.set_email_validate_token('register', email)
    tasks.add_task(worker.email.send_register_email, email, token)
    return BasicResponse()


@router.post('/validate/reset-password', response_model=BasicResponse)
async def reset_password(tasks: BackgroundTasks, form: EmailValidateForm):
    email = form.email
    member = await member_ctl.get_member(email=email)
    if not member:
        return BasicResponse()
    token = await credential_ctl.set_email_validate_token('reset_password', email)
    tasks.add_task(worker.email.send_reset_email, email, token)
    return BasicResponse()


class SendExternalForm(BaseModel):
    external_type: Optional[str] = 'QQ'
    external_id: str


@requires(['login'], 401)
@router.post('/validate/send-external', response_model=BasicResponse)
async def send_external(request: Request, tasks: BackgroundTasks, form: SendExternalForm):
    if form.external_type != 'QQ':
        raise auth_error.InvalidExternalTypeError()
    member = await member_ctl.get_member_by_external(ExternalType.QQ, form.external_id)
    if member:
        raise auth_error.ExternalIDUsedError()
    member_externals = await member_ctl.get_member_externals(request.user.id)
    if ExternalType.QQ in member_externals:
        raise auth_error.AlreadyBindExternalError()
    external_id = form.external_id
    if not external_id.isdigit():
        raise auth_error.InvalidExternalIDError()
    token = ''.join([str(secrets.choice(range(10))) for _ in range(6)])
    email = f'{external_id}@qq.com'
    await credential_ctl.set_email_validate_token('bind_external', email, token=f'{request.user.id}:{token}')
    tasks.add_task(worker.email.send_bind_external_email, email, token)
    return BasicResponse()


class ValidateExternalForm(BaseModel):
    external_type: Optional[str] = 'QQ'
    external_id: str
    validate_token: str


@requires(['login'], 401)
@router.post('/validate/external', response_model=BasicResponse)
async def validate_external(request: Request, form: ValidateExternalForm):
    if form.external_type != 'QQ':
        raise auth_error.InvalidExternalTypeError()
    member = await member_ctl.get_member_by_external(ExternalType.QQ, form.external_id)
    if member:
        raise auth_error.ExternalIDUsedError()
    member_externals = await member_ctl.get_member_externals(request.user.id)
    if ExternalType.QQ in member_externals:
        raise auth_error.AlreadyBindExternalError()
    external_id = form.external_id
    email = f'{external_id}@qq.com'
    token = f'{request.user.id}:{form.validate_token}'
    if credential_ctl.get_email_validate_token('bind_external', token) != email:
        raise auth_error.InvalidValidateTokenError()
    await member_ctl.bind_member_external_id(request.user.id, ExternalType.QQ, external_id)
    return BasicResponse()
