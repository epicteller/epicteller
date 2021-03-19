#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import datetime
from datetime import timezone

from epicteller.core.config import Config
from epicteller.core.dao.message import MessageDAO
from epicteller.core.mysql import Tables
from epicteller.core.util.enum import MessageType
from epicteller.core.util.seq import get_id

dndlog = Tables(user=Config.MYSQL_USERNAME, password=Config.MYSQL_PASSWORD,
                host=Config.MYSQL_HOST, port=int(Config.MYSQL_PORT), database='dndlog')


async def main():
    query = "SELECT * FROM chat"
    r = await dndlog.execute(query)
    rs = await r.fetchall()
    for row in rs:
        created = int(row.time.replace(tzinfo=timezone.utc).timestamp())
        dt = datetime.datetime.fromtimestamp(created)
        if row.type not in ('dice', 'chat'):
            continue
        _type = MessageType[row.type.upper()]
        await MessageDAO.create_message(
            row.ep_id, row.qq_id, _type, row.chat_text,
            get_id() if _type is MessageType.DICE else None,
            created,
        )
        print(f'{dt}\t{row.ep_id}\t{row.name}\t{row.chat_text}')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
