#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict

from epicteller.core.controller import campaign as campaign_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.core.model.episode import Episode as CoreEpisode
from epicteller.web.model.episode import Episode as WebEpisode


async def batch_fetch_episode(episodes: Dict[int, CoreEpisode]) -> Dict[int, WebEpisode]:
    room_ids = {e.room_id for e in episodes.values()}
    rooms = await room_ctl.batch_get_room(list(room_ids))
    campaign_ids = {e.campaign_id for e in episodes.values()}
    campaigns = await campaign_ctl.batch_get_campaign(list(campaign_ids))
    results = {}
    for eid, e in episodes.items():
        if not e:
            continue
        room = rooms.get(e.room_id)
        campaign = campaigns.get(e.campaign_id)
        result = WebEpisode(
            id=e.url_token,
            room_id=room.url_token if room else None,
            campaign_id=campaign.url_token if campaign else None,
            title=e.title,
            state=e.state.name.lower(),
            started_at=e.started_at,
            ended_at=e.ended_at,
            created=e.created,
            updated=e.updated,
        )
        results[eid] = result
    return results
