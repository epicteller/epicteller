#!/usr/bin/env python
# -*- coding: utf-8 -*-
import secrets
import string
import time
from typing import Optional

from epicteller.core.config import Config
from epicteller.core.dao.credential import CredentialDAO
from epicteller.core.model.credential import Credential


async def create_access_credential(member_id: int) -> Credential:
    token = secrets.token_urlsafe(32)
    lifetime = Config.ACCESS_TOKEN_LIFETIME
    now = int(time.time())
    credential = Credential(member_id=member_id, token=token, created_at=now, lifetime=lifetime)
    await CredentialDAO.set_access_credential(credential)
    return credential


async def revoke_access_credential(token: str):
    await CredentialDAO.revoke_access_credential(token)


async def get_access_credential(token: str) -> Optional[Credential]:
    return await CredentialDAO.get_access_credential(token)


async def refresh_access_credential(credential: Credential):
    credential.lifetime += Config.ACCESS_TOKEN_LIFETIME
    await CredentialDAO.set_access_credential(credential)


async def set_email_validate_token(action: str, email: str, *, token: Optional[str] = None) -> str:
    if token is None:
        token = secrets.token_urlsafe(32)
    await CredentialDAO.set_email_validate_token(action, token, email)
    return token


async def get_email_validate_token(action: str, token: str) -> Optional[str]:
    return await CredentialDAO.get_email_validate_token(action, token)
