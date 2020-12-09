#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiocqhttp import Event
from nonebot import on_command, Bot
from nonebot.typing import Matcher

from epicteller.core import error
from epicteller.core.controller import campaign as campaign_ctl
from epicteller.core.controller import episode as episode_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.core.controller import member as member_ctl
from epicteller.core.model.campaign import Campaign
from epicteller.core.model.episode import Episode
from epicteller.core.model.room import Room
from epicteller.core.util import const
from epicteller.core.util.enum import ExternalType, EpisodeState

start = on_command('start')


@start.handle()
async def _(bot: Bot, event: Event, state: dict):
    await must_prepare_context(start, bot, event, state)
    room: Room = state.get('room')
    campaign: Campaign = state.get('campaign')

    last_episode_id = campaign.last_episode_id
    last_episode = await episode_ctl.get_episode(last_episode_id)
    if not last_episode or last_episode.state == EpisodeState.ENDED:
        try:
            episode = await episode_ctl.start_new_episode(room, campaign)
        except error.episode.EpisodeRunningError as e:
            await start.finish('❌ 现在已经有一个章节在进行中啦！')
        await start.send('—— 🎬 新章开始 🎬 ——')
    else:
        episode = await episode_ctl.get_episode(campaign.last_episode_id)
        try:
            await episode_ctl.resume_episode(episode)
        except error.episode.EpisodeEndedError as e:
            await start.finish('❌ 章节已经结束啦。')
        except error.episode.EpisodeRunningError as e:
            await start.finish('❌ 这个章节已经在进行中啦！')
        await start.finish('—— 🎬 继续剧情  🎬 ——')


end = on_command('end')


@end.handle()
async def _(bot: Bot, event: Event, state: dict):
    await must_prepare_context(end, bot, event, state)
    room: Room = state.get('room')
    episode = await episode_ctl.get_room_running_episode(room)
    state['episode'] = episode
    episode: Episode = state.get('episode')
    if not episode:
        await end.finish('❌ 章节已经结束了哦。')
    await episode_ctl.end_episode(episode)
    await end.send('—— 💤 章节结束 💤 ——')
    possible_title = str(event.message).strip()
    if possible_title or episode.title != const.DEFAULT_EPISODE_TITLE:
        title = possible_title or episode.title
        if possible_title:
            await episode_ctl.rename_episode(episode, title)
        await end.finish(f"✨ 章节名已保存为「{title}」")
    else:
        await end.pause('🤔 看起来你还没有给刚刚结束的章节起一个名字，请直接回复你所拟定好的标题。\n'
                        f'如果暂时没想好，请回复任意的空白字符，标题会以「{episode.title}」为名保存。')


@end.got('title')
async def process_title(bot: Bot, event: Event, state: dict):
    episode: Episode = state.get('episode')
    possible_title = str(state['title']).strip()
    if not possible_title:
        await end.finish(f"✔️看起来你暂时还没有想好合适的标题，章节暂时以「{episode.title}」为名保存。\n"
                         f"如果之后有了合适的想法，也可以在网站上直接修改标题。")
    else:
        await episode_ctl.rename_episode(episode, possible_title)
        await end.finish(f"✨ 章节名已保存为「{possible_title}」啦！\n"
                         f"如果之后还有更好的想法，也可以在网站上继续修改标题。")


pause = on_command('pause', aliases={'save'})


@pause.handle()
async def _(bot: Bot, event: Event, state: dict):
    await must_prepare_context(pause, bot, event, state)
    room: Room = state.get('room')
    campaign: Campaign = state.get('campaign')
    episode = await episode_ctl.get_room_running_episode(room)
    if not episode:
        await pause.finish('❌ 章节已经结束了哦。')
    await episode_ctl.pause_episode(episode)
    await pause.send('—— 💾 保存进度 💾 ——')


async def must_prepare_context(matcher: Matcher, bot: Bot, event: Event, state: dict):
    if event.detail_type != 'group':
        await matcher.finish('🚫 这个指令只能在群聊中使用。')
    if 'anonymous' in event.raw_event and event.raw_event['anonymous']:
        await matcher.finish('🚫 这个指令不能在匿名状态下使用。')
    room_external_id = str(event.group_id)
    member_external_id = str(event.user_id)
    room = await room_ctl.get_room_by_external(ExternalType.QQ, room_external_id)
    if not room:
        await matcher.finish('⛔ 看起来这个群聊还没有绑定房间。\n'
                             '请在网站上创建房间并绑定该群聊后再试试吧。')
    member = await member_ctl.get_member_by_external(ExternalType.QQ, member_external_id)
    campaign = await campaign_ctl.get_campaign(room.current_campaign_id)
    if not campaign:
        await matcher.finish('⛔ 房间内还没有已就绪的战役。\n'
                             '请在网站上创建一个战役，或是将一个已有的战役设为「当前战役」后再试试。')
    if not member or member.id != campaign.owner_id:
        await matcher.finish('⛔ 没有权限使用该指令哦！')

    state['room'] = room
    state['member'] = member
    state['campaign'] = campaign
