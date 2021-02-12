#!/usr/bin/env python
# -*- coding: utf-8 -*-
from epicteller.core.error.base import EpictellerError


class MessageError(EpictellerError):
    code = 30000


class MessageCannotEditError(MessageError):
    code = 30001
    message = '该消息不支持编辑'
