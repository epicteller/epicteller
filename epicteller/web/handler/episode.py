#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from fastapi import APIRouter
from fastapi import Request

from epicteller.core.controller import message as message_ctl
from epicteller.web.controller.paging import generate_paging_info
from epicteller.web.fetcher import message as message_fetcher
from epicteller.web.model import PagingResponse
from epicteller.web.model.message import Message as WebMessage

router = APIRouter()


@router.get('/episodes/{episode_id}/messages', response_model=PagingResponse[WebMessage])
async def get(r: Request, episode_id: int,
              before: Optional[str] = None, after: Optional[str] = None, around: Optional[str] = None,
              limit: Optional[int] = 50):
    before_id: Optional[int] = None
    if before:
        before_msg = await message_ctl.get_message(url_token=before)
        before_id = before_msg.id if before_msg else None
    after_id: Optional[int] = None
    # after == '' 语义：取章节最开始的消息
    if after is not None:
        after_msg = await message_ctl.get_message(url_token=after)
        after_id = after_msg.id if after_msg else 0
    around_id: Optional[int] = None
    if around:
        around_msg = await message_ctl.get_message(url_token=around)
        around_id = around_msg.id if around_msg else None
    messages = await message_ctl.get_episode_messages(episode_id,
                                                      before=before_id,
                                                      after=after_id,
                                                      around=around_id,
                                                      limit=limit)
    is_end = len(messages) < limit
    web_message_map = await message_fetcher.batch_fetch_message({m.id: m for m in messages})
    web_messages = [web_message_map.get(m.id) for m in messages]
    paging_info = await generate_paging_info(
        r,
        before=web_messages[0].id if (around or before) and len(web_messages) else None,
        after=web_messages[-1].id if (around or after) and len(web_messages) else None,
        limit=limit,
        is_end=is_end,
    )
    return PagingResponse[WebMessage](data=web_messages, paging=paging_info)
