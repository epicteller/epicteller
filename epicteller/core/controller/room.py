#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Iterable, Dict, Union

from epicteller.core.dao.room import RoomDAO, RoomExternalDAO
from epicteller.core.model.room import Room, RoomExternalInfo
from epicteller.core.util.enum import ExternalType


async def get_room(room_id: Optional[int]=None, *,
                   url_token: Optional[str]=None) -> Optional[Room]:
    if room_id:
        return (await RoomDAO.batch_get_room_by_id([room_id])).get(room_id)
    elif url_token:
        return (await RoomDAO.batch_get_room_by_url_token([url_token])).get(url_token)
    return None


async def batch_get_room(room_ids: Iterable[int]=None, *,
                         url_tokens: Iterable[str]=None) -> Dict[Union[int, str], Room]:
    if room_ids:
        return await RoomDAO.batch_get_room_by_id(room_ids)
    elif url_tokens:
        return await RoomDAO.batch_get_room_by_url_token(url_tokens)
    return {}


async def get_room_by_external(external_type: ExternalType, external_id: str) -> Optional[Room]:
    room_id = await RoomExternalDAO.get_room_id_by_external(external_type, external_id)
    if not room_id:
        return None
    return await get_room(room_id)


async def get_room_external_info(room_id: int, external_type: ExternalType) -> Optional[RoomExternalInfo]:
    info_map = await RoomExternalDAO.get_external_infos_by_room(room_id)
    return info_map.get(external_type)


async def bind_room_external(room_id: int, external_type: ExternalType, external_id: str, bot_id: str):
    await RoomExternalDAO.bind_room_external_id(room_id, external_type, external_id, bot_id)


async def unbind_room_external(room_id: int, external_type: ExternalType):
    await RoomExternalDAO.unbind_room_external_id(room_id, external_type)


async def create_room(owner_id: int, name: str, description: str='', avatar: str='') -> Room:
    return await RoomDAO.create_room(name, description, owner_id, avatar)
