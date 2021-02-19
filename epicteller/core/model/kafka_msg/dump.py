#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from epicteller.core.model.kafka_msg import base
from epicteller.core.model.kafka_msg.base import KafkaMsg


@base.action
class MsgReceiveDump(KafkaMsg):
    action = 'epicteller.dump.receive_dump'
    runtime_id: str
    dump: Optional[bytes] = None
