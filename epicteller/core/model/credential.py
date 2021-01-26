#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import time
from dataclasses import dataclass

from jose import jwt
from pydantic import BaseModel

from epicteller.core.config import Config


class Credential(BaseModel):
    member_id: int
    token: str
    created_at: int
    lifetime: int

    @property
    def ttl(self):
        return max(self.expired_at - int(time.time()), 0)

    @property
    def expired_at(self) -> int:
        return self.created_at + self.lifetime

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expired_at

    @property
    def is_stale(self) -> bool:
        return self.ttl < Config.ACCESS_TOKEN_LIFETIME / 2

    @property
    def jwt(self) -> str:
        data = {
            'sub': self.token,
            'exp': datetime.datetime.fromtimestamp(self.expired_at),
            'iat': datetime.datetime.fromtimestamp(self.created_at),
            'nbf': datetime.datetime.fromtimestamp(self.created_at),
        }
        encoded_jwt = jwt.encode(data, Config.SECRET_KEY, access_token=self.token)
        return encoded_jwt
