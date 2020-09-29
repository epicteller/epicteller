#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from os import path

import nonebot

from epicteller.bot import bus, get_bot

bot = get_bot()
app = bot.asgi


def main():
    loop = asyncio.get_event_loop()
    loop.create_task(bus.run())

    nonebot.run(host='0.0.0.0', port=10090, loop=loop, debug=True)


if __name__ == '__main__':
    main()
