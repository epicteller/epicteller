#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Dict

from epicteller.core.model.room import Room as CoreRoom
from epicteller.core.util import imghosting
from epicteller.web.model.room import Room as WebRoom


async def fetch_room(room: CoreRoom) -> Optional[WebRoom]:
    if not room:
        return
    return (await batch_fetch_room({room.id: room})).get(room.id)


async def batch_fetch_room(rooms: Dict[int, CoreRoom]) -> Dict[int, WebRoom]:
    results = {}
    for rid, r in rooms.items():
        if not r:
            continue
        result = WebRoom(
            id=r.url_token,
            name=r.name,
            description=r.description,
            is_removed=r.is_removed,
            avatar=imghosting.get_avatar_url(r.avatar),
            created=r.created,
            updated=r.updated,
        )
        results[r.id] = result
    return results
