#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from fastapi import APIRouter, Request, Depends

from epicteller.core.controller import campaign as campaign_ctl
from epicteller.core.controller import character as character_ctl
from epicteller.core.controller import episode as episode_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.core.error.base import NotFoundError
from epicteller.core.model.campaign import Campaign
from epicteller.web.middleware.auth import requires
from epicteller.web.model import PagingResponse
from epicteller.web.model.campaign import Campaign as WebCampaign, CreateCampaignParam
from epicteller.web.model.character import Character as WebCharacter
from epicteller.web.fetcher import campaign as campaign_fetcher
from epicteller.web.fetcher import character as character_fetcher
from epicteller.web.fetcher import episode as episode_fetcher
from epicteller.web.model.episode import Episode as WebEpisode

router = APIRouter()


async def prepare(url_token: str) -> Campaign:
    campaign = await campaign_ctl.get_campaign(url_token=url_token)
    if not campaign:
        raise NotFoundError()
    return campaign


@router.post('/campaigns', response_model=WebCampaign, response_model_exclude_none=True)
@requires(['login'])
async def create_campaign(r: Request, param: CreateCampaignParam):
    login_id: int = r.user.id
    url_token = param.room_id
    room = await room_ctl.get_room(url_token=url_token)
    if not room:
        raise NotFoundError()
    campaign = await campaign_ctl.create_campaign(login_id, room.id, param.name, param.description)
    await campaign_ctl.active_campaign(campaign)
    return await campaign_fetcher.fetch_campaign(campaign)


@router.get('/campaigns/{url_token}', response_model=WebCampaign, response_model_exclude_none=True)
async def get_campaign(r: Request, campaign: Campaign = Depends(prepare)):
    web_campaign = await campaign_fetcher.fetch_campaign(campaign, r.user.id)
    return web_campaign


@router.get('/campaigns/{url_token}/episodes', response_model=PagingResponse[WebEpisode],
            response_model_exclude_none=True)
async def get_campaign_episodes(r: Request, campaign: Campaign = Depends(prepare),
                                offset: Optional[int] = 0, limit: Optional[int] = 100):
    episodes = await episode_ctl.get_episodes_by_campaign(campaign.id)
    web_episode_map = await episode_fetcher.batch_fetch_episode({e.id: e for e in episodes})
    web_episodes = [web_episode_map.get(e.id) for e in episodes]
    return PagingResponse[WebEpisode](data=web_episodes).dict(exclude_none=True)


@router.get('/campaigns/{url_token}/characters', response_model=PagingResponse[WebCharacter],
            response_model_exclude_none=True)
async def get_campaign_characters(r: Request, campaign: Campaign = Depends(prepare)):
    character_ids = await character_ctl.get_character_ids_by_campaign(campaign.id)
    characters = await character_ctl.batch_get_character(character_ids)
    web_character_map = await character_fetcher.batch_fetch_character(characters, login_id=r.user.id)
    web_characters = [web_character_map.get(cid) for cid in character_ids]
    return PagingResponse[WebCharacter](data=web_characters).dict(exclude_none=True)
