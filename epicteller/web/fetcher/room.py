#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Dict

from epicteller.core.controller import member as member_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.core.model.room import Room as CoreRoom
from epicteller.core.util import imghosting
from epicteller.web.fetcher import member as member_fetcher
from epicteller.web.model.room import Room as WebRoom


async def fetch_room(room: CoreRoom) -> Optional[WebRoom]:
    if not room:
        return
    return (await batch_fetch_room({room.id: room})).get(room.id)


async def batch_fetch_room(rooms: Dict[int, CoreRoom]) -> Dict[int, WebRoom]:
    room_ids = [r.id for r in rooms.values()]
    owner_ids = [r.owner_id for r in rooms.values()]
    members = await member_ctl.batch_get_member(owner_ids)
    owner_map = await member_fetcher.batch_fetch_members(members)
    count_map = await room_ctl.batch_get_member_count_by_room(room_ids)
    results = {}
    for rid, r in rooms.items():
        if not r:
            continue
        result = WebRoom(
            id=r.url_token,
            name=r.name,
            description=r.description,
            owner=owner_map.get(r.owner_id),
            is_removed=r.is_removed,
            avatar=imghosting.get_avatar_url(r.avatar),
            created=r.created,
            updated=r.updated,
            member_count=count_map.get(r.id),
            has_running_campaign=bool(r.current_campaign_id),
        )
        results[r.id] = result
    return results
