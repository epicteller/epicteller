#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import IntEnum


class CampaignState(IntEnum):
    PREPARING = 0
    ACTIVE = 1
    ARCHIVED = 2


class EpisodeState(IntEnum):
    RUNNING = 0
    PAUSED = 1
    ENDED = 2


class DiceType(IntEnum):
    SCALAR = 1
    ARRAY = 2
    CHECK = 3


class MessageType(IntEnum):
    CHAT = 1
    DICE = 2
