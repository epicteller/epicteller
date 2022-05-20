#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from typing import Optional, Iterable, Dict, Union, List

from epicteller.core.dao.campaign import CampaignDAO
from epicteller.core.dao.character import CharacterCampaignDAO, CharacterDAO
from epicteller.core.dao.room import RoomDAO
from epicteller.core.model.campaign import Campaign
from epicteller.core.model.room import Room
from epicteller.core.tables import table
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


async def get_campaigns_by_room(room: Room, after: int = 0, limit: int = 20) -> List[Campaign]:
    campaign_ids = await CampaignDAO.get_campaign_ids_by_room(room.id, after, limit)
    campaign_map = await batch_get_campaign(campaign_ids)
    return [campaign_map.get(cid) for cid in campaign_ids]


async def get_campaign_count_by_room(room: Room) -> int:
    count_map = await CampaignDAO.batch_get_campaign_count_by_room([room.id])
    return count_map.get(room.id, 0)


async def get_participated_campaigns(member_id: int) -> List[Campaign]:
    characters = await CharacterDAO.get_characters_by_owner(member_id)
    character_ids = [c.id for c in characters]
    character_campaign_id_map, owned_campaign_ids = await asyncio.gather(
        CharacterCampaignDAO.get_campaign_ids_by_character_ids(character_ids),
        CampaignDAO.get_campaign_ids_by_owner(member_id),
    )
    campaign_ids = set()
    for cids in character_campaign_id_map.values():
        campaign_ids.update(cids)
    campaign_ids.update(owned_campaign_ids)
    campaign_ids = list(campaign_ids)
    campaign_map = await batch_get_campaign(campaign_ids)
    campaigns = [campaign_map.get(cid) for cid in campaign_map]
    campaigns.sort(key=lambda c: c.updated, reverse=True)
    return campaigns


async def active_campaign(campaign: Campaign) -> Campaign:
    campaign.state = CampaignState.ACTIVE
    async with table.db.begin():
        await CampaignDAO.update_campaign(campaign.id, state=int(CampaignState.ACTIVE))
        await RoomDAO.update_room(campaign.room_id, current_campaign_id=campaign.id)
    return campaign


async def archive_campaign(campaign: Campaign) -> Campaign:
    campaign.state = CampaignState.ARCHIVED
    async with table.db.begin():
        await CampaignDAO.update_campaign(campaign.id, state=int(CampaignState.ARCHIVED))
        await RoomDAO.update_room(campaign.room_id, current_campaign_id=0)
    return campaign


async def create_campaign(owner_id: int, room_id: int, name: str, description: str='') -> Campaign:
    campaign = await CampaignDAO.create_campaign(room_id, name, description, owner_id)
    await RoomDAO.update_room(room_id, current_campaign_id=campaign.id)
    return campaign
