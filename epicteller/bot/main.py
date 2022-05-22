#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.onebot.v11 import Adapter

from epicteller.bot import bus_init
from epicteller.core import redis


def main():
    nonebot.init(command_start={'/', '!', "！"})
    driver = nonebot.get_driver()
    driver.register_adapter(Adapter)
    nonebot.load_plugin('nonebot_plugin_sentry')
    nonebot.load_plugins('epicteller/bot/plugin')
    nonebot.get_driver().on_startup(redis.pool.init)
    nonebot.get_driver().on_startup(bus_init)

    nonebot.run(host='0.0.0.0', port=10090)


if __name__ == '__main__':
    main()
