#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from epicteller.core import redis
from epicteller.core.model.credential import Credential


class CredentialDAO:
    r = redis.redis

    @classmethod
    async def create_access_credential(cls, credential: Credential):
        await cls.r.set(f'access_token:{credential.token}', credential.to_json(), expire=credential.ttl)

    @classmethod
    async def create_refresh_credential(cls, credential: Credential):
        await cls.r.set(f'refresh_token:{credential.token}', credential.to_json(), expire=credential.ttl)

    @classmethod
    async def revoke_access_credential(cls, token: str):
        await cls.r.expire(f'access_token:{token}', 10)

    @classmethod
    async def revoke_refresh_credential(cls, token: str):
        await cls.r.expire(f'refresh_token:{token}', 10)

    @classmethod
    async def get_access_credential(cls, token: str) -> Optional[Credential]:
        data = await cls.r.get(f'access_token:{token}')
        if not data:
            return
        return Credential.from_json(data)

    @classmethod
    async def get_refresh_credential(cls, token: str) -> Optional[Credential]:
        data = await cls.r.get(f'refresh_token:{token}')
        if not data:
            return
        return Credential.from_json(data)
