#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from epicteller.core import redis
from epicteller.core.model.credential import Credential


class CredentialDAO:
    r = redis.pool

    @classmethod
    async def set_access_credential(cls, credential: Credential):
        await cls.r.pool.set(f'access_token:{credential.token}', credential.json(), expire=credential.ttl)

    @classmethod
    async def revoke_access_credential(cls, token: str):
        await cls.r.pool.expire(f'access_token:{token}', 10)

    @classmethod
    async def set_email_validate_token(cls, action: str, token: str, email: str):
        await cls.r.pool.set(f'email_validate:{action}:{token}', email, expire=600)

    @classmethod
    async def get_email_validate_token(cls, action: str, token: str) -> Optional[str]:
        email = await cls.r.pool.get(f'email_validate:{action}:{token}')
        if not email:
            return
        return email.decode('utf8')

    @classmethod
    async def get_access_credential(cls, token: str) -> Optional[Credential]:
        data = await cls.r.pool.get(f'access_token:{token}')
        if not data:
            return
        return Credential.parse_raw(data)
