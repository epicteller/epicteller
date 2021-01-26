#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from starlette.authentication import AuthenticationBackend
from fastapi import Request


class AuthBackend(AuthenticationBackend):
    async def authenticate(self, request: Request):
        session_id: Optional[str] = request.cookies.get('q_c0')
        if not session_id:
            return
        try:

