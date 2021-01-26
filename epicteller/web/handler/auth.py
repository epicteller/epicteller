#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Body, Depends, BackgroundTasks, Response
from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr

from epicteller.core.controller import credential as credential_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.web import worker
from epicteller.web.error.auth import IncorrectEMailPasswordError, UnauthorizedError, EMailUsedError, EMailValidateError
from epicteller.web.controller import auth as auth_web_ctl
from epicteller.web.model import BasicResponse

router = APIRouter()


class RegisterForm(BaseModel):
    email: EmailStr
    validate_token: str
    password: str = Field(min_length=10, max_length=50)
    name: str


@router.post('/register')
async def register(register_form: RegisterForm, r: Response):
    member = await member_ctl.get_member(email=register_form.email)
    if member:
        raise EMailUsedError()
    email = await credential_ctl.get_email_validate_token(register_form.validate_token)
    if email != register_form.email:
        raise EMailValidateError()
    member = await member_ctl.create_member(name=register_form.name,
                                            email=register_form.email,
                                            password=register_form.password)
    await auth_web_ctl.create_credential(r, member.id)


class LoginForm(BaseModel):
    email: EmailStr
    password: str


@router.post('/login')
async def login(login_form: LoginForm, r: Response):
    email = login_form.email
    password = login_form.password
    member = await member_ctl.check_member_email_password(email, password)
    if not member:
        return IncorrectEMailPasswordError()
    await auth_web_ctl.create_credential(r, member.id)


@router.post('/logout', response_model=BasicResponse)
async def logout(access_token: str = Body(...), refresh_token: str = Body(...)):
    await credential_ctl.revoke_access_credential(access_token)
    return BasicResponse()


@router.post('/email-validate', response_model=BasicResponse)
async def email_validate(tasks: BackgroundTasks, email: EmailStr = Body(..., embed=True)):
    member = await member_ctl.get_member(email=email)
    if member:
        raise EMailUsedError()
    token = await credential_ctl.set_email_validate_token(email)
    tasks.add_task(worker.email.send_register_email, email, token)
    return BasicResponse()
