#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from fastapi import APIRouter, Request

from epicteller.core.controller import campaign as campaign_ctl
from epicteller.core.controller import character as character_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.web.controller.paging import generate_paging_info
from epicteller.web.fetcher import campaign as campaign_fetcher
from epicteller.web.fetcher import character as character_fetcher
from epicteller.web.fetcher.member import fetch_me
from epicteller.web.fetcher import room as room_fetcher
from epicteller.web.middleware.auth import requires
from epicteller.web.model import BasicResponse, PagingResponse
from epicteller.web.model.member import MeSettings, Me
from epicteller.web.model.campaign import Campaign as WebCampaign
from epicteller.web.model.character import Character as WebCharacter
from epicteller.web.model.room import Room as WebRoom

router = APIRouter()


@router.get('/me', response_model=Me, response_model_exclude_none=True)
@requires(['login'])
async def me(r: Request):
    member_id = r.user.id
    member = await member_ctl.get_member(member_id)
    return await fetch_me(member)


@router.put('/me', response_model=BasicResponse)
@requires(['login'])
async def update_me_settings(r: Request, settings: MeSettings):
    member_id = r.user.id
    setting_dict = settings.dict(exclude_unset=True)
    await member_ctl.update_member(member_id, **setting_dict)
    return BasicResponse()


@router.get('/me/rooms', response_model=PagingResponse[WebRoom], response_model_exclude_none=True)
@requires(['login'])
async def my_rooms(r: Request, after: Optional[str] = None, offset: Optional[int] = 0, limit: Optional[int] = 20):
    member_id = r.user.id
    after_id = 0
    if after_room := await room_ctl.get_room(url_token=after):
        after_id = after_room.id
    room_ids = await room_ctl.get_room_ids_by_member(member_id, after_id, limit)
    rooms = await room_ctl.batch_get_room(room_ids)
    total = await room_ctl.get_room_count_by_member(member_id)
    web_rooms_map = await room_fetcher.batch_fetch_room(rooms)
    web_rooms = [web_rooms_map.get(rid) for rid in room_ids]
    paging = await generate_paging_info(r,
                                        after=rooms[-1].url_token if len(rooms) > 0 else None,
                                        offset=offset, limit=limit, total=total)
    return PagingResponse[WebRoom](data=web_rooms, paging=paging)


@router.get('/me/characters', response_model=PagingResponse[WebCharacter], response_model_exclude_none=True)
@requires(['login'])
async def my_characters(r: Request):
    member_id = r.user.id
    characters = await character_ctl.get_characters_by_owner(member_id)
    web_characters_map = await character_fetcher.batch_fetch_character({c.id: c for c in characters})
    web_characters = [web_characters_map.get(c.id) for c in characters]
    return PagingResponse(data=web_characters)


@router.get('/me/campaigns', response_model=PagingResponse[WebCampaign], response_model_exclude_none=True)
@requires(['login'])
async def my_campaigns(r: Request):
    member_id = r.user.id
    campaigns = await campaign_ctl.get_participated_campaigns(member_id)
    campaign_ids = [c.id for c in campaigns]
    campaign_map = {c.id: c for c in campaigns}
    web_campaigns = await campaign_fetcher.batch_fetch_campaign(campaign_map, member_id)
    web_campaigns_list = [web_campaigns.get(cid) for cid in campaign_ids]
    return PagingResponse(data=web_campaigns_list)
