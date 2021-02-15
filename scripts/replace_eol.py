#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio

from epicteller.core.dao.message import MessageDAO
from epicteller.core.model.message import TextMessageContent
from epicteller.core.util.enum import MessageType


async def main():
    start = 0
    limit = 1000
    while messages := await MessageDAO.scan_messages(start, limit):
        for message in messages:
            print(f'message {message.id}', end='')
            if message.type != MessageType.TEXT:
                print(f'...skip, not text')
                continue
            assert isinstance(message.content, TextMessageContent)
            print(f'[{message.content.text[:30]}]', end='')
            replaced_text = message.content.text.replace('\r\n', '\n')
            if replaced_text == message.content.text:
                print(f'...skip, equally')
                continue
            content = TextMessageContent(text=replaced_text)
            await MessageDAO.update_message(message.id, content=content.dict(), updated=message.created)
            print(f'...replaced')
        start += limit
    print('Done')


if __name__ == '__main__':
    asyncio.run(main())
