#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict, Any

from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND


class EpictellerError(HTTPException):
    status_code = HTTP_403_FORBIDDEN
    message: str = 'Epicteller Error'
    code: int = 10000
    detail: Any = None

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __init__(self, *, message: str = None, code: int = None):
        if message:
            self.message = message
        if code:
            self.code = code


class ForbiddenError(EpictellerError):
    status_code = code = HTTP_403_FORBIDDEN
    message = 'Forbidden Error'


class NotFoundError(EpictellerError):
    status_code = code = HTTP_404_NOT_FOUND
    message = '资源未找到'

