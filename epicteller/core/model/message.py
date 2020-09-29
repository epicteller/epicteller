#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional

from epicteller.core.util.enum import MessageType, DiceType
from epicteller.core.util.typing import DiceValue_T


@dataclass
class MessageContent:
    pass


@dataclass
class TextMessageContent(MessageContent):
    text: str


@dataclass
class ImageMessageContent(MessageContent):
    image: str


@dataclass
class DiceMessageContent(MessageContent):
    dice_type: DiceType
    reason: Optional[str]
    expression: str
    detail: str
    value: DiceValue_T

    def __post_init__(self):
        self.dice_type = DiceType(self.dice_type)


@dataclass
class Message:
    id: int
    url_token: str
    episode_id: int
    character_id: int
    is_removed: bool
    is_gm: bool
    type: MessageType
    content: MessageContent
    created: int
    updated: int
