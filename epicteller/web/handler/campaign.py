#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Request

from epicteller.core.controller import campaign as campaign_ctl
from epicteller.core.error.base import NotFoundError
from epicteller.web.model.campaign import Campaign as WebCampaign
from epicteller.web.fetcher import campaign as campaign_fetcher

router = APIRouter()


@router.get('/campaigns/{url_token}', response_model=WebCampaign, response_model_exclude_none=True)
async def get_campaign(url_token: str):
    campaign = await campaign_ctl.get_campaign(url_token=url_token)
    if not campaign:
        raise NotFoundError()
    web_campaign = await campaign_fetcher.fetch_campaign(campaign)
    return web_campaign

