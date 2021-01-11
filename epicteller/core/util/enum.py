#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import IntEnum


class CampaignState(IntEnum):
    PREPARING = 0
    ACTIVE = 1
    ARCHIVED = 2


class EpisodeState(IntEnum):
    PENDING = 0
    RUNNING = 1
    PAUSED = 2
    ENDED = 3


class CombatState(IntEnum):
    INITIATING = 0
    RUNNING = 1
    ENDED = 2


class DiceType(IntEnum):
    SCALAR = 1
    ARRAY = 2
    CHECK = 3


class MessageType(IntEnum):
    TEXT = 1
    IMAGE = 2
    DICE = 3


class ExternalType(IntEnum):
    QQ = 1
