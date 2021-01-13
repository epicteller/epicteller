#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Iterable, Dict, Union

from epicteller.core.dao.campaign import CampaignDAO
from epicteller.core.dao.episode import EpisodeDAO
from epicteller.core.dao.room import RoomRunningEpisodeDAO
from epicteller.core import error
from epicteller.core.model.campaign import Campaign
from epicteller.core.model.episode import Episode
from epicteller.core.model.room import Room
from epicteller.core.tables import table
from epicteller.core.util import const
from epicteller.core.util.enum import EpisodeState


async def get_episode(episode_id: Optional[int]=None, *,
                      url_token: Optional[str]=None) -> Optional[Episode]:
    if episode_id:
        return (await EpisodeDAO.batch_get_episode_by_id([episode_id])).get(episode_id)
    elif url_token:
        return (await EpisodeDAO.batch_get_episode_by_url_token([url_token])).get(url_token)
    return None


async def batch_get_episode(episode_ids: Iterable[int]=None, *,
                            url_tokens: Iterable[str]=None) -> Dict[Union[int, str], Episode]:
    if episode_ids:
        return await EpisodeDAO.batch_get_episode_by_id(episode_ids)
    elif url_tokens:
        return await EpisodeDAO.batch_get_episode_by_url_token(url_tokens)
    return {}


async def start_new_episode(room: Room, campaign: Campaign, title: str=const.DEFAULT_EPISODE_TITLE) -> Episode:
    running_episode_id = await RoomRunningEpisodeDAO.get_running_episode_id(room.id)
    if running_episode_id:
        raise error.episode.EpisodeRunningError()
    async with table.db.begin():
        episode = await EpisodeDAO.create_episode(room.id, campaign.id, title, state=EpisodeState.RUNNING)
        await RoomRunningEpisodeDAO.set_running_episode(room.id, episode.id)
        await CampaignDAO.update_campaign(campaign.id, last_episode_id=episode.id)
    return episode


async def resume_episode(episode: Episode):
    if episode.state == EpisodeState.ENDED:
        raise error.episode.EpisodeEndedError()
    elif episode.state == EpisodeState.RUNNING:
        raise error.episode.EpisodeRunningError()

    running_episode_id = await RoomRunningEpisodeDAO.get_running_episode_id(episode.room_id)
    if running_episode_id:
        raise error.episode.EpisodeRunningError()
    async with table.db.begin():
        await EpisodeDAO.update_episode(episode.id, state=int(EpisodeState.RUNNING))
        await RoomRunningEpisodeDAO.set_running_episode(episode.room_id, episode.id)
        await CampaignDAO.update_campaign(episode.campaign_id, last_episode_id=episode.id)


async def pause_episode(episode: Episode):
    running_episode_id = await RoomRunningEpisodeDAO.get_running_episode_id(episode.room_id)
    async with table.db.begin():
        await EpisodeDAO.update_episode(episode.id, state=int(EpisodeState.PAUSED))
        if running_episode_id == episode.id:
            await RoomRunningEpisodeDAO.remove_running_episode(episode.room_id)
        await CampaignDAO.update_campaign(episode.campaign_id, last_episode_id=episode.id)


async def end_episode(episode: Episode):
    running_episode_id = await RoomRunningEpisodeDAO.get_running_episode_id(episode.room_id)
    async with table.db.begin():
        await EpisodeDAO.update_episode(episode.id,
                                        state=int(EpisodeState.ENDED))
        if running_episode_id == episode.id:
            await RoomRunningEpisodeDAO.remove_running_episode(episode.room_id)
        await CampaignDAO.update_campaign(episode.campaign_id, last_episode_id=0)


async def rename_episode(episode: Episode, title: str):
    await EpisodeDAO.update_episode(episode.id, title=title)


async def get_room_running_episode(room: Room) -> Optional[Episode]:
    episode_id = await RoomRunningEpisodeDAO.get_running_episode_id(room.id)
    if not episode_id:
        return None
    return await get_episode(episode_id)
