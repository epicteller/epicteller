#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict, Any

from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND


class EpictellerError(HTTPException):
    status_code = HTTP_403_FORBIDDEN
    message: str = 'Epicteller Error'
    code: int = 10000
    headers: Dict[str, Any] = None

    def _get_detail(self):
        return {
            'name': self.__class__.__name__,
            'message': self.message,
            'code': self.code,
        }

    def __init__(self, message: str = None, headers: Dict[str, Any] = None):
        if message:
            self.message = message
        if headers:
            self.headers = headers
        super().__init__(status_code=self.status_code, detail=self._get_detail(), headers=self.headers)


class ForbiddenError(EpictellerError):
    status_code = code = HTTP_403_FORBIDDEN
    message = 'Forbidden Error'


class NotFoundError(EpictellerError):
    status_code = code = HTTP_404_NOT_FOUND
    message = '资源未找到'

