#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import Request, Response

from epicteller.core.config import Config
from epicteller.core.controller import credential as credential_ctl


async def create_credential(req: Request, resp: Response, member_id: int):
    access_credential = await credential_ctl.create_access_credential(member_id)
    secure = not Config.DEBUG
    resp.set_cookie('q_c0',
                    access_credential.token,
                    max_age=365 * 86400,
                    expires=365 * 86400,
                    secure=secure,
                    httponly=True,
                    samesite='Lax')


async def revoke_credential(r: Response):
    r.delete_cookie('q_c0', path='/')
