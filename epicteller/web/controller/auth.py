#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel

from epicteller.core.config import Config
from epicteller.core.controller import credential as credential_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.core.model.member import Member
from epicteller.web.error.auth import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


class CredentialPair(BaseModel):
    access_token: str
    refresh_token: str


async def get_current_member(token: str = Depends(oauth2_scheme)) -> Member:
    unauthorized_exception = UnauthorizedError()
    credential = await credential_ctl.get_access_credential(token)
    if not credential or credential.is_expired:
        raise unauthorized_exception
    member = await member_ctl.get_member(credential.member_id)
    if not member:
        raise unauthorized_exception
    return member


async def create_credential_pair(member_id: int) -> CredentialPair:
    access_credential = await credential_ctl.create_access_credential(member_id)
    refresh_credential = await credential_ctl.create_refresh_credential(member_id)
    return CredentialPair(access_token=access_credential.jwt, refresh_token=refresh_credential.jwt)
