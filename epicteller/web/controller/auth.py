#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from epicteller.core.config import Config
from epicteller.core.controller import credential as credential_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.core.model.member import Member
from epicteller.web.error.auth import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_member(token: str = Depends(oauth2_scheme)) -> Member:
    unauthorized_exception = UnauthorizedError()
    try:
        payload = jwt.decode(token, Config.SECRET_KEY)
        access_token: str = payload.get('sub')
        if not access_token:
            raise unauthorized_exception
    except JWTError:
        raise unauthorized_exception
    credential = await credential_ctl.get_access_credential(token)
    if not credential or credential.is_expired:
        raise unauthorized_exception
    member = await member_ctl.get_member(credential.member_id)
    if not member:
        raise unauthorized_exception
    return member
