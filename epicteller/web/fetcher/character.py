#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict, Optional

from epicteller.core.model.character import Character as CoreCharacter
from epicteller.core.util import imghosting
from epicteller.web.model.character import Character as WebCharacter


async def fetch_character(character: CoreCharacter) -> Optional[WebCharacter]:
    if not character:
        return
    return (await batch_fetch_characters({character.id: character})).get(character.url_token)


async def batch_fetch_characters(characters: Dict[int, CoreCharacter]) -> Dict[str, WebCharacter]:
    results = {}
    for cid, c in characters.items():
        if not c:
            continue
        result = WebCharacter(
            id=c.url_token,
            name=c.name,
            avatar=imghosting.get_avatar_url(c.avatar),
            description=c.description,
            is_removed=c.is_removed or None,
            raw_data=c.raw_data,
            created=c.created,
            updated=c.updated,
        )
        results[result.id] = result
    return results
