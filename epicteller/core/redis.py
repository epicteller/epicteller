#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aioredis

from epicteller.core.config import Config
from epicteller.core.log import logger


class Pool:
    def __init__(self, url: str, **kwargs):
        self.url = url
        self.kwargs = kwargs
        self._pool = None

    async def init(self):
        if self._pool:
            return
        try:
            self._pool = await aioredis.create_redis_pool(self.url, **self.kwargs)
        except Exception as e:
            logger.error(f'Connecting redis error: {e}')
            raise e

    @property
    def pool(self):
        return self._pool


pool = Pool(Config.REDIS_URL, minsize=1, maxsize=10, timeout=1)
