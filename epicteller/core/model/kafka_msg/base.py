#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from typing import Dict, Type, Optional, ClassVar

from pydantic import BaseModel, Field


class KafkaMsg(BaseModel):
    action: ClassVar[str]
    action_time: float = Field(default_factory=time.time)
    operator_id: int = 0


_msg_model_map: Dict[str, KafkaMsg] = {}


def action(cls: KafkaMsg):
    if hasattr(cls, 'action'):
        topic = cls.action
    else:
        topic = cls.__fields__['action'].get_default()
    _msg_model_map[topic] = cls
    return cls


def get_msg_model(topic: str) -> Optional[KafkaMsg]:
    return _msg_model_map.get(topic)
