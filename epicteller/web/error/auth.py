#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Any, Dict

from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED


class IncorrectEMailPasswordError(HTTPException):
    status_code = HTTP_403_FORBIDDEN
    detail = '邮箱或密码不正确'

    def __init__(self, detail: Any = detail, headers: Dict[str, Any] = None):
        super().__init__(status_code=self.status_code, detail=detail, headers=headers)


class UnauthorizedError(HTTPException):
    status_code = HTTP_401_UNAUTHORIZED
    detail = '登录凭据失效'
    headers = {'WWW-Authenticate': 'Bearer'}

    def __init__(self, detail: Any = detail, headers: Dict[str, Any] = None):
        super().__init__(status_code=self.status_code, detail=detail, headers=headers)


class EMailUsedError(HTTPException):
    status_code = HTTP_403_FORBIDDEN
    detail = '邮箱已被占用'

    def __init__(self, detail: Any = detail, headers: Dict[str, Any] = None):
        super().__init__(status_code=self.status_code, detail=detail, headers=headers)


class EMailValidateError(HTTPException):
    status_code = HTTP_403_FORBIDDEN
    detail = '邮箱验证失败'

    def __init__(self, detail: Any = detail, headers: Dict[str, Any] = None):
        super().__init__(status_code=self.status_code, detail=detail, headers=headers)
