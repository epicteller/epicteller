#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import asdict
from typing import Optional, List, Iterable, Dict, Union

from epicteller.core.dao.message import MessageDAO
from epicteller.core.model.character import Character
from epicteller.core.model.episode import Episode
from epicteller.core.model.message import Message, MessageContent
from epicteller.core.util.enum import MessageType


async def get_message(message_id: Optional[int]=None, *,
                      url_token: Optional[str]=None) -> Optional[Message]:
    if message_id:
        return (await MessageDAO.batch_get_message_by_id([message_id])).get(message_id)
    if url_token:
        return (await MessageDAO.batch_get_message_by_url_token([url_token])).get(url_token)
    return None


async def batch_get_message(message_ids: Iterable[int]=None, *,
                            url_tokens: Iterable[str]=None) -> Dict[Union[int, str], Message]:
    if message_ids:
        return await MessageDAO.batch_get_message_by_id(message_ids)
    if url_tokens:
        return await MessageDAO.batch_get_message_by_url_token(url_tokens)
    return {}


async def get_episode_messages(episode_id: int, *,
                               oldest: Optional[int]=None, latest: Optional[int]=None,
                               limit: int=40) -> List[Message]:
    if oldest is not None:
        return await MessageDAO.get_episode_messages_from_oldest(episode_id, oldest, limit)
    elif latest is not None:
        return await MessageDAO.get_episode_messages_to_latest(episode_id, latest, limit)
    return await MessageDAO.get_episode_latest_messages(episode_id, limit)


async def create_message(episode: Episode, character: Optional[Character], message_type: MessageType,
                         content: MessageContent, is_gm: bool=False) -> Message:
    content_data: dict = content.dict()
    if is_gm:
        character_id = 0
    else:
        character_id = character.id
    return await MessageDAO.create_message(episode.id, character_id, message_type, content_data, is_gm)


async def remove_message(message_id: int):
    await MessageDAO.update_message(message_id, is_removed=1)


async def recover_message(message_id: int):
    await MessageDAO.update_message(message_id, is_removed=0)
