#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict, Optional

from epicteller.core.controller import campaign as campaign_ctl
from epicteller.core.controller import character as character_ctl
from epicteller.core.controller import episode as episode_ctl
from epicteller.core.model.message import Message as CoreMessage, ImageMessageContent, DiceMessageContent
from epicteller.core.util import imghosting
from epicteller.web.fetcher import character as character_fetcher
from epicteller.web.model.message import Message as WebMessage


async def batch_fetch_message(messages: Dict[int, CoreMessage]) -> Dict[int, WebMessage]:
    character_ids = {m.character_id for m in messages.values()}
    core_character_map = await character_ctl.batch_get_character(list(character_ids))
    character_map = await character_fetcher.batch_fetch_character(core_character_map)
    episode_ids = {m.episode_id for m in messages.values()}
    core_episode_map = await episode_ctl.batch_get_episode(list(episode_ids))
    campaign_ids = {m.campaign_id for m in messages.values()}
    core_campaign_map = await campaign_ctl.batch_get_campaign(list(campaign_ids))

    results = {}
    for mid, m in messages.items():
        if not m:
            continue
        episode = core_episode_map.get(m.episode_id)
        episode_url_token: Optional[str] = None
        if episode:
            episode_url_token = episode.url_token
        campaign = core_campaign_map.get(m.campaign_id)
        campaign_url_token: Optional[str] = None
        if campaign:
            campaign_url_token = campaign.url_token
        content = m.content
        if isinstance(content, ImageMessageContent):
            content.image = imghosting.get_full_url(content.image)
        elif isinstance(content, DiceMessageContent):
            content.dice_type = content.dice_type.name.lower()
        result = WebMessage(
            id=m.url_token,
            campaign_id=campaign_url_token,
            episode_id=episode_url_token,
            character=character_map.get(m.character_id),
            is_gm=m.is_gm,
            message_type=m.type.name.lower(),
            content=content,
            created=m.created,
            updated=m.updated,
        )
        results[mid] = result
    return results
