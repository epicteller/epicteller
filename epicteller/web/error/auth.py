#!/usr/bin/env python
# -*- coding: utf-8 -*-
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from epicteller.core.error.base import EpictellerError


class IncorrectEMailPasswordError(EpictellerError):
    message = '邮箱或密码不正确'


class UnauthorizedError(EpictellerError):
    status_code = HTTP_401_UNAUTHORIZED
    message = '登录凭据失效'
    headers = {'WWW-Authenticate': 'Bearer'}


class EMailUsedError(EpictellerError):
    message = '邮箱已被占用'


class EMailValidateError(EpictellerError):
    message = '邮箱验证失败'
