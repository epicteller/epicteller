#!/usr/bin/env python
# -*- coding: utf-8 -*-
import secrets
from typing import Optional

from fastapi import APIRouter, Request, BackgroundTasks, Response, Query
from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr

from epicteller.core.controller import credential as credential_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.core import worker
from epicteller.core.log import logger
from epicteller.core.util.enum import ExternalType
from epicteller.web.error import auth as auth_error
from epicteller.web.controller import auth as auth_web_ctl
from epicteller.web.middleware.auth import User, requires
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
async def register(tasks: BackgroundTasks, req: Request, resp: Response, form: RegisterForm):
    email = await credential_ctl.get_email_validate_token('register', form.validate_token)
    if not email:
        raise auth_error.InvalidValidateTokenError()
    member = await member_ctl.get_member(email=email)
    if member:
        raise auth_error.EMailUsedError()
    member = await member_ctl.create_member(name=form.name,
                                            email=email,
                                            password=form.password)
    await auth_web_ctl.create_credential(req, resp, member.id)
    tasks.add_task(worker.external.bind_member_character, member.id)
    return BasicResponse()


class LoginForm(BaseModel):
    email: EmailStr
    password: str


@router.post('/login', response_model=BasicResponse)
async def login(req: Request, resp: Response, login_form: LoginForm):
    email = login_form.email
    password = login_form.password
    member = await member_ctl.check_member_email_password(email, password)
    if not member:
        raise auth_error.IncorrectEMailPasswordError()
    await auth_web_ctl.create_credential(req, resp, member.id)
    return BasicResponse()


@router.post('/logout', response_model=BasicResponse)
@requires(['login'])
async def logout(req: Request, resp: Response):
    if req.user.id == 0:
        return BasicResponse()
    user: User = req.user
    await credential_ctl.revoke_access_credential(user.access_token)
    await auth_web_ctl.revoke_credential(resp)
    return BasicResponse()


class ResetPasswordForm(BaseModel):
    password: str = Field(min_length=10, max_length=50)
    validate_token: str


@router.post('/reset-password', response_model=BasicResponse)
async def reset_password(form: ResetPasswordForm):
    email = await credential_ctl.get_email_validate_token('reset_password', form.validate_token)
    if not email:
        raise auth_error.InvalidValidateTokenError()
    member = await member_ctl.get_member(email=email)
    await member_ctl.change_member_password(member.id, form.password)
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


@router.post('/validate/reset-password-email', response_model=BasicResponse)
async def send_reset_password_email(tasks: BackgroundTasks, form: EmailValidateForm):
    email = form.email
    member = await member_ctl.get_member(email=email)
    if not member:
        logger.warning(f'Member not found: {email}')
        return BasicResponse()
    token = await credential_ctl.set_email_validate_token('reset_password', email)
    tasks.add_task(worker.email.send_reset_email, email, token)
    return BasicResponse()


class SendExternalForm(BaseModel):
    external_type: Optional[str] = 'QQ'
    external_id: str


@router.post('/validate/send-external-email', response_model=BasicResponse)
@requires(['login'])
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


@router.post('/bind-external', response_model=BasicResponse)
@requires(['login'])
async def validate_external(tasks: BackgroundTasks, request: Request, form: ValidateExternalForm):
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
    if await credential_ctl.get_email_validate_token('bind_external', token) != email:
        raise auth_error.InvalidValidateTokenError(message='验证码输入错误')
    await member_ctl.bind_member_external_id(request.user.id, ExternalType.QQ, external_id)
    tasks.add_task(worker.external.bind_member_character, request.user.id)
    return BasicResponse()
