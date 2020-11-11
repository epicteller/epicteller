#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import struct
from random import random

from nonebot import on_command, permission, CommandSession


@on_command('p', permission=permission.PRIVATE_FRIEND)
async def predict(session: CommandSession):
    feed = [random.randbits(32) for _ in range(624)]
    packed_feed = struct.pack('624I', feed)
    b64_feed = base64.b64encode(packed_feed)
    await session.send(b64_feed)
