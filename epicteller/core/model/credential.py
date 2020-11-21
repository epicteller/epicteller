#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import time
from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin
from jose import jwt

from epicteller.core.config import Config


@dataclass
class Credential(DataClassJsonMixin):
    member_id: int
    token: str
    created_at: int
    ttl: int

    @property
    def expired_at(self) -> int:
        return self.created_at + self.ttl

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expired_at

    @property
    def is_stale(self) -> bool:
        return time.time() > self.created_at + self.ttl / 2

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
