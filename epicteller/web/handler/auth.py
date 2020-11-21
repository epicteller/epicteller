#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Body, Depends
from jose import jwt, JWTError
from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import validate_email, EmailStr

from epicteller.core.config import Config
from epicteller.core.controller import credential as credential_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.web.error.auth import IncorrectEMailPasswordError, UnauthorizedError

router = APIRouter()


class RegisterForm(BaseModel):
    email: EmailStr
    validate_token: str
    password: str = Field(min_length=8, max_length=50)
    name: str


@router.post('/register')
async def register(register_form: RegisterForm):
    pass


class LoginForm(BaseModel):
    email: EmailStr
    password: str


@router.post('/login')
async def login(login_form: LoginForm):
    email = login_form.email
    password = login_form.password
    member = await member_ctl.check_member_email_password(email, password)
    if not member:
        return IncorrectEMailPasswordError()
    access_credential = await credential_ctl.create_access_credential(member.id)
    refresh_credential = await credential_ctl.create_refresh_credential(member.id)
    return {
        'access_token': access_credential.jwt,
        'refresh_token': refresh_credential.jwt,
    }


@router.post('/refresh')
async def refresh(token: str = Body(...)):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY)
        refresh_token: str = payload.get('sub')
        if not refresh_token:
            return UnauthorizedError(detail='Invalid token.')
    except JWTError:
        return UnauthorizedError(detail='Invalid token.')
    refresh_credential = await credential_ctl.get_refresh_credential(refresh_token)
    if not refresh_credential or refresh_credential.is_expired:
        return UnauthorizedError(detail='Credential expired.')
    access_credential = await credential_ctl.create_access_credential(refresh_credential.member_id)
    if refresh_credential.is_stale:
        await credential_ctl.revoke_refresh_credential(refresh_credential.token)
        refresh_credential = await credential_ctl.create_refresh_credential(refresh_credential.member_id)
    return {
        'access_token': access_credential.jwt,
        'refresh_token': refresh_credential.jwt,
    }
