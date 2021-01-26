#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from fastapi import Request

from epicteller.core.controller import credential as credential_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.core.model.member import Member
from epicteller.web.error.auth import UnauthorizedError


async def get_login_id(request: Request) -> Optional[int]:
    session_id: Optional[str] = request.cookies.get('q_c0')
    if not session_id:
        return 0
    credential = await credential_ctl.get_access_credential(session_id)
    if not credential or credential.is_expired:
        return 0
    if credential.is_stale:
        await credential_ctl.refresh_access_credential(credential)
    return credential.member_id


async def create_credential_pair(member_id: int) -> CredentialPair:
    access_credential = await credential_ctl.create_access_credential(member_id)
    refresh_credential = await credential_ctl.create_refresh_credential(member_id)
    return CredentialPair(access_token=access_credential.jwt, refresh_token=refresh_credential.jwt)
