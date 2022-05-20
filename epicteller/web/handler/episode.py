#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi import Request

from epicteller.core.controller import campaign as campaign_ctl
from epicteller.core.controller import episode as episode_ctl
from epicteller.core.controller import message as message_ctl
from epicteller.core.error.base import NotFoundError
from epicteller.core.model.episode import Episode
from epicteller.web.controller.paging import generate_paging_info
from epicteller.web.error.permission import PermissionDeniedError
from epicteller.web.fetcher import message as message_fetcher
from epicteller.web.middleware.auth import requires
from epicteller.web.model import PagingResponse, BasicResponse
from epicteller.web.model.episode import Episode as WebEpisode, UpdateEpisode
from epicteller.web.model.message import Message as WebMessage

router = APIRouter()


async def prepare(url_token: str):
    episode = await episode_ctl.get_episode(url_token=url_token)
    if not episode or episode.is_removed:
        raise NotFoundError()
    return episode


@router.get('/episodes/{url_token}/messages',
            response_model=PagingResponse[WebMessage],
            response_model_exclude_none=True)
async def get(r: Request, episode: Episode = Depends(prepare),
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
    messages = await message_ctl.get_episode_messages(episode.id,
                                                      before=before_id,
                                                      after=after_id,
                                                      around=around_id,
                                                      limit=limit)
    is_end = len(messages) < limit
    web_message_map = await message_fetcher.batch_fetch_message({m.id: m for m in messages}, r.user.id)
    web_messages = [web_message_map.get(m.id) for m in messages]
    paging_info = await generate_paging_info(
        r,
        before=web_messages[0].id if (around or before or
                                      (not around and not before and after is None)
                                      ) and len(web_messages) else None,
        after=web_messages[-1].id if (around or after is not None) and len(web_messages) else None,
        limit=limit,
        is_end=is_end,
    )
    return PagingResponse[WebMessage](data=web_messages, paging=paging_info).dict(exclude_none=True)


@router.put('/episodes/{url_token}',
            response_model=BasicResponse,
            response_model_exclude_none=True)
@requires(['login'])
async def update_episode(r: Request, update: UpdateEpisode,
                         episode: Episode = Depends(prepare)):
    member_id = r.user.id
    campaign = await campaign_ctl.get_campaign(episode.campaign_id)
    if not campaign:
        raise NotFoundError()
    if campaign.owner_id != member_id:
        raise PermissionDeniedError()
    update_dict = update.dict(exclude_unset=True)
    await episode_ctl.update_episode(episode, **update_dict)
    return BasicResponse()
