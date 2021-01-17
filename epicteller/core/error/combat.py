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
    message = '当前战斗已经进入行动阶段'
    code = 10002


class CombatNotRunningError(CombatError):
    message = '战斗并未处于行动阶段'
    code = 10003


class CombatEndedError(CombatError):
    message = '当前战斗已结束'
    code = 10004


class CombatOrderEmptyError(CombatError):
    message = '先攻顺位为空'
    code = 10005


class CombatTokenChangedError(CombatError):
    message = '重排先攻列表时，不能增减顺位数量'
    code = 10006


class CannotRemoveActingTokenError(CombatError):
    message = '无法移除正处于行动轮的战斗者'
    code = 10007


class CombatTokenAlreadyExistsError(CombatError):
    message = '战斗者已存在于先攻顺位'
    code = 10008


class CombatTokenNotFoundError(CombatError):
    message = '找不到战斗者'
    code = 10009
