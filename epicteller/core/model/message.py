#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from nonebot.adapters.cqhttp import MessageSegment
from pydantic import BaseModel

from epicteller.core.util import imghosting
from epicteller.core.util.enum import MessageType, DiceType
from epicteller.core.util.typing import DiceValue_T


class MessageContent(BaseModel):
    def to_message(self) -> MessageSegment:
        raise NotImplementedError


class TextMessageContent(MessageContent):
    text: str

    def to_message(self):
        return MessageSegment.text(self.text)


class ImageMessageContent(MessageContent):
    image: str

    def to_message(self):
        image_url = imghosting.get_full_url(self.image)
        return MessageSegment.image(image_url)


class DiceMessageContent(MessageContent):
    dice_type: DiceType
    reason: Optional[str]
    expression: str
    detail: str
    value: DiceValue_T

    def __post_init__(self):
        self.dice_type = DiceType(self.dice_type)

    def to_message(self):
        reason: str = ''
        if self.reason:
            reason = f" ({self.reason})"
        return MessageSegment.text(f"[骰子{reason}: {self.expression} = {self.value}]")


class Message(BaseModel):
    id: int
    url_token: str
    campaign_id: int
    episode_id: int
    character_id: int
    is_removed: bool
    is_gm: bool
    type: MessageType
    content: MessageContent
    created: int
    updated: int
