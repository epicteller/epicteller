#!/usr/bin/env python
# -*- coding: utf-8 -*-

from epicteller.core.config import Config
from epicteller.core.mysql import Tables

table = Tables(url=Config.MYSQL_URL)


async def init():
    await table.init()
