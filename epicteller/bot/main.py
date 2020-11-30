#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio

import nonebot

from epicteller.bot import start_bus
from epicteller.core import redis


def main():
    nonebot.init(debug=True)
    nonebot.load_builtin_plugins()
    nonebot.load_plugins('plugin')
    nonebot.get_driver().on_startup(redis.pool.init)
    nonebot.get_driver().on_startup(start_bus)

    nonebot.run(host='0.0.0.0', port=10090)


if __name__ == '__main__':
    main()
