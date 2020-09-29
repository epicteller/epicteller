#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Iterable, Dict, Union

from epicteller.core.dao.character import CharacterDAO, CharacterExternalDAO
from epicteller.core.model.campaign import Campaign
from epicteller.core.model.character import Character
from epicteller.core.model.member import Member
from epicteller.core.util.enum import ExternalType


async def get_character(character_id: Optional[int]=None, *,
                        url_token: Optional[str]=None) -> Optional[Character]:
    if character_id:
        return (await CharacterDAO.batch_get_character_by_id([character_id])).get(character_id)
    elif url_token:
        return (await CharacterDAO.batch_get_character_by_url_token([url_token])).get(url_token)
    return None


async def batch_get_character(character_ids: Iterable[int]=None, *,
                              url_tokens: Optional[str]=None) -> Dict[Union[int, str], Character]:
    if character_ids:
        return await CharacterDAO.batch_get_character_by_id(character_ids)
    elif url_tokens:
        return await CharacterDAO.batch_get_character_by_url_token(url_tokens)


async def get_character_by_campaign_name(campaign: Campaign, name: str) -> Optional[Character]:
    return await CharacterDAO.get_character_by_campaign_name(campaign.id, name)


async def check_character_external(character: Character, external_type: ExternalType, external_id: str) -> bool:
    external_map = await CharacterExternalDAO.get_external_ids_by_character(character.id)
    if external_type not in external_map:
        await CharacterExternalDAO.bind_character_external_id(character.id, external_type, external_id)
        return True
    elif external_map[external_type] == external_id:
        return True
    else:
        return False


async def bind_character_member(character: Character, member: Member):
    await CharacterDAO.update_character(character.id, member_id=member.id)


async def bind_character_external(character: Character, external_type: ExternalType, external_id: str):
    await CharacterExternalDAO.bind_character_external_id(character.id, external_type, external_id)


async def create_character(campaign: Campaign, name: str, member: Optional[Member]=None,
                           avatar: str='', description: str='') -> Character:
    member_id = member.id if member else 0
    return await CharacterDAO.create_character(member_id, campaign.id, name, avatar, description, {})
