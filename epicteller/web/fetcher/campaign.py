#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import itertools
from typing import Dict, Optional, List

from epicteller.core.controller import character as character_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.core.model.campaign import Campaign as CoreCampaign
from epicteller.web.fetcher import character as character_fetcher
from epicteller.web.fetcher import member as member_fetcher
from epicteller.web.model.campaign import Campaign as WebCampaign, CampaignRelationship
from epicteller.web.model.character import Character as WebCharacter


async def fetch_campaign(campaign: CoreCampaign, login_id: int = 0) -> Optional[WebCampaign]:
    if not campaign:
        return None
    return (await batch_fetch_campaign({campaign.id: campaign}, login_id)).get(campaign.id)


async def batch_fetch_campaign(campaigns: Dict[int, CoreCampaign], login_id: int = 0) -> Dict[int, WebCampaign]:
    owner_ids = {c.owner_id for c in campaigns.values()}
    core_owner_map = await member_ctl.batch_get_member(list(owner_ids))
    web_owner_map = await member_fetcher.batch_fetch_members(core_owner_map)
    room_ids = {c.room_id for c in campaigns.values()}
    rooms = await room_ctl.batch_get_room(list(room_ids))

    campaign_ids = [cid for cid in campaigns.keys()]
    campaign_character_ids = await asyncio.gather(*[character_ctl.get_character_ids_by_campaign(cid)
                                                    for cid in campaign_ids])
    campaign_character_ids_map = {cid: character_ids
                                  for cid, character_ids in zip(campaign_ids, campaign_character_ids)}
    character_map = await character_ctl.batch_get_character(list(set(itertools.chain(*campaign_character_ids))))
    web_character_map = await character_fetcher.batch_fetch_character(character_map)
    campaign_characters_map: Dict[int, List[WebCharacter]] = {
        campaign_id: [web_character_map.get(character_id)
                      for character_id in campaign_character_ids_map.get(campaign_id, [])]
        for campaign_id in campaign_ids
    }

    results = {}
    for cid, c in campaigns.items():
        if not c:
            continue
        room = rooms.get(c.room_id)
        characters = campaign_characters_map.get(cid, [])
        result = WebCampaign(
            id=c.url_token,
            room_id=room.url_token if room else None,
            name=c.name,
            description=c.description,
            owner=web_owner_map.get(c.owner_id),
            state=c.state.name.lower(),
            created=c.created,
            updated=c.updated,
            characters=characters,
        )
        if login_id:
            relationship = CampaignRelationship(is_gm=login_id == c.owner_id)
            if my_characters := [c for c in character_map.values()
                                 if c.member_id == login_id and c.id in campaign_character_ids_map.get(cid, [])]:
                character = web_character_map.get(my_characters[-1].id)
                relationship.using_character = character
                relationship.is_player = character is not None
            result.relationship = relationship
        results[cid] = result
    return results
