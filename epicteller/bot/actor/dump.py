#!/usr/bin/env python
# -*- coding: utf-8 -*-
from epicteller.bot import bus
from epicteller.core.config import Config
from epicteller.core.controller import dice as dice_ctl
from epicteller.core.model.kafka_msg.dump import MsgReceiveDump


@bus.on('epicteller.dump.receive_dump')
async def receive_dump(topic: str, data: str):
    msg = MsgReceiveDump.parse_raw(data)
    if Config.RUNTIME_ID != msg.runtime_id:
        return
    await dice_ctl.receive_memory_dump(msg.dump)
