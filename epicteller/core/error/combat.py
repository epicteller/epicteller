#!/usr/bin/env python
# -*- coding: utf-8 -*-
from epicteller.core.error.base import EpictellerError


class CombatError(EpictellerError):
    pass


class CombatNotFoundError(CombatError):
    pass


class CombatRunningError(CombatError):
    pass


class CombatNotRunningError(CombatError):
    pass


class CombatEndedError(CombatError):
    pass


class CombatOrderEmptyError(CombatError):
    pass


class CombatTokenChangedError(CombatError):
    pass


class CannotRemoveActingTokenError(CombatError):
    def __init__(self, token_name: str):
        self.token_name = token_name


class CombatTokenAlreadyExistsError(CombatError):
    def __init__(self, token_name: str):
        self.token_name = token_name


class CombatTokenNotFoundError(CombatError):
    def __init__(self, token_name: str):
        self.token_name = token_name
