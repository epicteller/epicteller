#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging

from loguru import logger as logger_

logger = logger_
"""
:说明:

  日志记录器对象。

:默认信息:

  * 格式: ``[%(asctime)s %(name)s] %(levelname)s: %(message)s``
  * 等级: ``DEBUG`` / ``INFO`` ，根据 config 配置改变
  * 输出: 输出至 stdout

:用法:

.. code-block:: python

    from epicteller.log import logger
"""

# default_handler = logging.StreamHandler(sys.stdout)
# default_handler.setFormatter(
#     logging.Formatter("[%(asctime)s %(name)s] %(levelname)s: %(message)s"))
# logger.addHandler(default_handler)


class Filter:

    def __init__(self) -> None:
        self.level = "DEBUG"

    def __call__(self, record):
        record["name"] = record["name"].split(".")[0]
        levelno = logger.level(self.level).no
        return record["level"].no >= levelno


class LoguruHandler(logging.Handler):

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth,
                   exception=record.exc_info).log(level, record.getMessage())


logger.remove()
default_filter = Filter()
default_format = (
    "<g>{time:MM-DD HH:mm:ss}</g> "
    "[<lvl>{level}</lvl>] "
    "<c><u>{name}</u></c> | "
    # "<c>{function}:{line}</c>| "
    "{message}")
logger.add(sys.stdout,
           colorize=True,
           diagnose=False,
           filter=default_filter,
           format=default_format)
