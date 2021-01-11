#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from pydantic import BaseModel, Field


class KafkaMsg(BaseModel):
    action: str
    action_time: float = Field(default_factory=time.time)
    operator_id: int = 0
