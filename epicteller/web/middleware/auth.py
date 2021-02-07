#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel
from starlette.authentication import AuthenticationBackend, AuthCredentials, BaseUser
from starlette.requests import HTTPConnection

from epicteller.core.controller import credential as credential_ctl


class User(BaseUser, BaseModel):
    id: int
    access_token: str

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return ''

    @property
    def identity(self) -> int:
        return self.id


class AuthBackend(AuthenticationBackend):
    async def authenticate(self, r: HTTPConnection):
        session_id: Optional[str] = r.cookies.get('q_c0')
        if not session_id:
            return AuthCredentials(), None
        credential = await credential_ctl.get_access_credential(session_id)
        if not credential or credential.is_expired:
            return AuthCredentials(), None
        if credential.is_stale:
            await credential_ctl.refresh_access_credential(credential)
        return AuthCredentials(['login']), User(id=credential.member_id, access_token=session_id)
