#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

import aioredis

from epicteller.core.config import Config

redis = None


async def init():
    global redis
    redis = await aioredis.create_redis_pool(Config.REDIS_URL, minsize=1, maxsize=10)


asyncio.get_event_loop().run_until_complete(init())
