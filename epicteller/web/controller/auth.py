#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import Response

from epicteller.core.controller import credential as credential_ctl


async def create_credential(r: Response, member_id: int):
    access_credential = await credential_ctl.create_access_credential(member_id)
    r.set_cookie('q_c0',
                 access_credential.token,
                 max_age=365 * 86400,
                 expires=365 * 86400,
                 path='/',
                 secure=True,
                 httponly=True,
                 samesite='lax')
