#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import hashlib
import struct
import random

import httpx
from nonebot import on_command, permission, CommandSession

from epicteller.core.util import imghosting


@on_command('p', permission=permission.PRIVATE_FRIEND)
async def predict(session: CommandSession):
    bucket = 'ep-predict-1251152679'
    token = f'{random.randint(0, 9999):04d}'
    feed = [random.getrandbits(32) for _ in range(624)]
    packed_feed = struct.pack('624I', *feed)
    m = hashlib.md5()
    m.update(packed_feed)
    md5 = base64.b64encode(m.digest()).decode()
    headers = {
        'Host': imghosting.config.get_host(bucket),
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(len(packed_feed)),
        'Content-MD5': md5,
    }
    target_url = imghosting.get_presigned_url(token, headers, bucket=bucket)
    async with httpx.AsyncClient() as http_client:
        r = await http_client.put(target_url, data=packed_feed, headers=headers)
        r.raise_for_status()
    await session.send(token)
