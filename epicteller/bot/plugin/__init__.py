#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

import typing
from nonebot import on_natural_language, NLPSession, IntentCommand

from epicteller.bot import regex_commands, get_bot

_ignore_patterns = [*get_bot().config.COMMAND_START, re.compile(r'^[()（）]')]


@on_natural_language(only_to_me=False, only_short_message=False)
async def _(session: NLPSession):
    raw_message = session.msg_text.strip()
    for regex, command in regex_commands:
        m = regex.search(raw_message)
        if not m:
            continue
        matched = m.group(0)
        return IntentCommand(100.0, command, current_arg=raw_message[len(matched):].strip())
    # Check message is not command-like object.
    for pattern in _ignore_patterns:
        if isinstance(pattern, typing.Pattern):
            m = pattern.search(raw_message)
            if m and m.start(0) == 0:
                return
        elif isinstance(pattern, str):
            if raw_message.startswith(pattern):
                return
    return IntentCommand(100.0, 'say', current_arg=session.msg)
