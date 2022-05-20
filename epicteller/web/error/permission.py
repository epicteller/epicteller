#!/usr/bin/env python
# -*- coding: utf-8 -*-
from starlette.status import HTTP_403_FORBIDDEN

from epicteller.core.error.base import EpictellerError


class PermissionDeniedError(EpictellerError):
    status_code = HTTP_403_FORBIDDEN
    message = '无此操作权限'
