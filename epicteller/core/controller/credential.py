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
    ttl = Config.ACCESS_TOKEN_TTL
    now = int(time.time())
    credential = Credential(member_id=member_id, token=token, created_at=now, ttl=ttl)
    await CredentialDAO.create_access_credential(credential)
    return credential


async def create_refresh_credential(member_id: int) -> Credential:
    token = secrets.token_urlsafe(32)
    ttl = Config.REFRESH_TOKEN_TTL
    now = int(time.time())
    credential = Credential(member_id=member_id, token=token, created_at=now, ttl=ttl)
    await CredentialDAO.create_refresh_credential(credential)
    return credential


async def revoke_access_credential(token: str):
    await CredentialDAO.revoke_access_credential(token)


async def revoke_refresh_credential(token: str):
    await CredentialDAO.revoke_refresh_credential(token)


async def get_access_credential(token: str) -> Optional[Credential]:
    return await CredentialDAO.get_access_credential(token)


async def get_refresh_credential(token: str) -> Optional[Credential]:
    return await CredentialDAO.get_refresh_credential(token)


async def set_email_validate_token(email: str) -> str:
    token = ''.join(secrets.choice(string.digits) for _ in range(6))
    await CredentialDAO.set_email_validate_token(token, email)
    return token


async def get_email_validate_token(token: str) -> Optional[str]:
    return await CredentialDAO.get_email_validate_token(token)
