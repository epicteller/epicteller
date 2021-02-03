#!/usr/bin/env python
# -*- coding: utf-8 -*-
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from epicteller.core.error.base import EpictellerError


class IncorrectEMailPasswordError(EpictellerError):
    message = '邮箱或密码不正确'


class UnauthorizedError(EpictellerError):
    status_code = HTTP_401_UNAUTHORIZED
    message = '登录凭据失效'
    code = 401


class EMailUsedError(EpictellerError):
    message = '邮箱已被占用'


class ExternalIDUsedError(EpictellerError):
    message = '外部帐号已被占用'


class EMailValidateError(EpictellerError):
    message = '邮箱验证失败'


class InvalidValidateTokenError(EpictellerError):
    message = '无效的邮箱验证凭据'


class InvalidExternalTypeError(EpictellerError):
    message = '未知外部帐号类型'


class InvalidExternalIDError(EpictellerError):
    message = '无效的外部帐号格式'


class AlreadyBindExternalError(ExternalIDUsedError):
    message = '已经绑定过外部帐号'
