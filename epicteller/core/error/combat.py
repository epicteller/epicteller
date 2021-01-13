#!/usr/bin/env python
# -*- coding: utf-8 -*-
from starlette.status import HTTP_404_NOT_FOUND

from epicteller.core.error.base import EpictellerError


class CombatError(EpictellerError):
    code = 10000


class CombatNotFoundError(CombatError):
    status_code = HTTP_404_NOT_FOUND
    code = 10001


class CombatRunningError(CombatError):
    code = 10002


class CombatNotRunningError(CombatError):
    code = 10003


class CombatEndedError(CombatError):
    code = 10004


class CombatOrderEmptyError(CombatError):
    code = 10005


class CombatTokenChangedError(CombatError):
    code = 10006


class CannotRemoveActingTokenError(CombatError):
    code = 10007


class CombatTokenAlreadyExistsError(CombatError):
    code = 10008


class CombatTokenNotFoundError(CombatError):
    code = 10009
