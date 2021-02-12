#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict, Optional

from epicteller.core.controller import member as member_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.core.model.campaign import Campaign as CoreCampaign
from epicteller.web.fetcher import member as member_fetcher
from epicteller.web.model.campaign import Campaign as WebCampaign


async def fetch_campaign(campaign: CoreCampaign) -> Optional[WebCampaign]:
    if not campaign:
        return None
    return (await batch_fetch_campaign({campaign.id: campaign})).get(campaign.id)


async def batch_fetch_campaign(campaigns: Dict[int, CoreCampaign]) -> Dict[int, WebCampaign]:
    owner_ids = {c.owner_id for c in campaigns.values()}
    core_owner_map = await member_ctl.batch_get_member(list(owner_ids))
    web_owner_map = await member_fetcher.batch_fetch_members(core_owner_map)
    room_ids = {c.room_id for c in campaigns.values()}
    rooms = await room_ctl.batch_get_room(list(room_ids))
    results = {}
    for cid, c in campaigns.items():
        if not c:
            continue
        room = rooms.get(c.room_id)
        result = WebCampaign(
            id=c.url_token,
            room_id=room.url_token if room else None,
            name=c.name,
            description=c.description,
            owner=web_owner_map.get(c.owner_id),
            state=c.state.name.lower(),
            created=c.created,
            updated=c.updated,
        )
        results[cid] = result
    return results
