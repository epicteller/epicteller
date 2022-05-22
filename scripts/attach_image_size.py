#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio

from epicteller.core.dao.message import MessageDAO
from epicteller.core.model.message import ImageMessageContent
from epicteller.core.util import imghosting


async def main():
    start_id = 0
    while messages := await MessageDAO.scan_messages(start_id):
        start_id = messages[-1].id
        print(start_id)
        messages = [m for m in messages if isinstance(m.content, ImageMessageContent)]
        for message in messages:
            assert isinstance(message.content, ImageMessageContent)
            content: ImageMessageContent = message.content
            if content.width:
                continue
            width, height = await imghosting.get_image_size(token=content.image)
            content.width = width
            content.height = height
            await MessageDAO.update_message(message.id, content=content.dict())
            print(content.image, width, height)


if __name__ == '__main__':
    asyncio.run(main())
