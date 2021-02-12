#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict, Optional

from epicteller.core.controller import member as member_ctl
from epicteller.core.model.character import Character as CoreCharacter
from epicteller.core.util import imghosting
from epicteller.web.fetcher import member as member_fetcher
from epicteller.web.model.character import Character as WebCharacter


async def fetch_character(character: CoreCharacter) -> Optional[WebCharacter]:
    if not character:
        return
    return (await batch_fetch_character({character.id: character})).get(character.id)


async def batch_fetch_character(characters: Dict[int, CoreCharacter]) -> Dict[int, WebCharacter]:
    member_ids = {c.member_id for c in characters.values()}
    member_ids.discard(0)
    core_member_map = await member_ctl.batch_get_member(list(member_ids))
    member_map = await member_fetcher.batch_fetch_members(core_member_map)
    results = {}
    for cid, c in characters.items():
        if not c:
            continue
        result = WebCharacter(
            id=c.url_token,
            name=c.name,
            avatar=imghosting.get_avatar_url(c.avatar),
            description=c.description,
            member=member_map.get(c.member_id),
            is_removed=c.is_removed or None,
            raw_data=c.raw_data,
            created=c.created,
            updated=c.updated,
        )
        results[c.id] = result
    return results
