#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from typing import Dict, Type, Optional

from pydantic import BaseModel, Field


class KafkaMsg(BaseModel):
    action: str
    action_time: float = Field(default_factory=time.time)
    operator_id: int = 0


_msg_model_map: Dict[str, Type[KafkaMsg]] = {}


def action(topic: str):
    def decorate(cls: Type[KafkaMsg]):
        cls.action = topic
        _msg_model_map[topic] = cls
        return cls
    return decorate


def get_msg_model(topic: str) -> Optional[Type[KafkaMsg]]:
    return _msg_model_map.get(topic)
