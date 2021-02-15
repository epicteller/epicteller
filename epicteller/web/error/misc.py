#!/usr/bin/env python
# -*- coding: utf-8 -*-
from starlette.status import HTTP_400_BAD_REQUEST

from epicteller.core.error.base import EpictellerError


class BadRequestError(EpictellerError):
    status_code = HTTP_400_BAD_REQUEST
    message = '数据格式非法'
