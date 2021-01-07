#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Iterable, Dict, Union

from epicteller.core.dao.campaign import CampaignDAO
from epicteller.core.dao.room import RoomDAO
from epicteller.core.model.campaign import Campaign
from epicteller.core.util.enum import CampaignState


async def get_campaign(campaign_id: Optional[int]=None, *,
                       url_token: Optional[str]=None) -> Optional[Campaign]:
    if campaign_id:
        return (await CampaignDAO.batch_get_campaign_by_id([campaign_id])).get(campaign_id)
    elif url_token:
        return (await CampaignDAO.batch_get_campaign_by_url_token([url_token])).get(url_token)
    return None


async def batch_get_campaign(campaign_ids: Iterable[int]=None, *,
                             url_tokens: Iterable[str]=None) -> Dict[Union[int, str], Campaign]:
    if campaign_ids:
        return await CampaignDAO.batch_get_campaign_by_id(campaign_ids)
    elif url_tokens:
        return await CampaignDAO.batch_get_campaign_by_url_token(url_tokens)
    return {}


async def active_campaign(campaign: Campaign):
    await CampaignDAO.update_campaign(campaign.id, state=int(CampaignState.ACTIVE))
    await RoomDAO.update_room(campaign.room_id, current_campaign_id=campaign.id)


async def archive_campaign(campaign: Campaign):
    await CampaignDAO.update_campaign(campaign.id, state=int(CampaignState.ARCHIVED))
    await RoomDAO.update_room(campaign.room_id, current_campaign_id=0)


async def create_campaign(owner_id: int, room_id: int, name: str, description: str='') -> Campaign:
    campaign = await CampaignDAO.create_campaign(room_id, name, description, owner_id)
    await RoomDAO.update_room(room_id, current_campaign_id=campaign.id)
    return campaign
