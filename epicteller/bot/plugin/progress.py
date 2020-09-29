#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nonebot import on_command, CommandSession

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


@on_command('start', only_to_me=False)
async def start(session: CommandSession):
    await must_prepare_context(session)
    room: Room = session.get('room')
    campaign: Campaign = session.get('campaign')

    last_episode_id = campaign.last_episode_id
    last_episode = await episode_ctl.get_episode(last_episode_id)
    if not last_episode or last_episode.state == EpisodeState.ENDED:
        try:
            episode = await episode_ctl.start_new_episode(room, campaign)
        except error.episode.EpisodeRunningError as e:
            session.finish('❌ 现在已经有一个章节在进行中啦！')
        await session.send('—— 🎬 新章开始 🎬 ——')
    else:
        episode = await episode_ctl.get_episode(campaign.last_episode_id)
        try:
            await episode_ctl.resume_episode(episode)
        except error.episode.EpisodeEndedError as e:
            session.finish('❌ 章节已经结束啦。')
        except error.episode.EpisodeRunningError as e:
            session.finish('❌ 这个章节已经在进行中啦！')
        await session.send('—— 🎬 继续剧情  🎬 ——')


@on_command('end', only_to_me=False)
async def end(session: CommandSession):
    if session.is_first_run:
        await must_prepare_context(session)
        room: Room = session.get('room')
        episode = await episode_ctl.get_room_running_episode(room)
        session.state['episode'] = episode
        episode: Episode = session.get('episode')
        if not episode:
            session.finish('❌ 章节已经结束了哦。')
        await episode_ctl.end_episode(episode)
        await session.send('—— 💤 章节结束 💤 ——')
        possible_title = session.current_arg_text.strip()
        if possible_title or episode.title != const.DEFAULT_EPISODE_TITLE:
            title = possible_title or episode.title
            if possible_title:
                await episode_ctl.rename_episode(episode, title)
            await session.send(f"✨ 章节已保存为「{title}」")
        else:
            session.pause('🤔 看起来你还没有给刚刚结束的章节起一个名字。\n'
                          '请直接回复你所拟定好的标题。如果暂时没想好，也可以回复任意的空白字符。')
        return
    episode: Episode = session.get('episode')
    possible_title = session.current_arg_text.strip()
    if not possible_title:
        session.finish(f"✔️看起来你暂时还没有想好合适的标题，章节暂时以「{episode.title}」为名保存。\n"
                       f"如果之后有了合适的想法，也可以在网站上直接修改标题。")
    else:
        await episode_ctl.rename_episode(episode, possible_title)
        session.finish(f"✨ 章节已保存为「{possible_title}」啦！\n"
                       f"如果之后还有更好的想法，也可以在网站上继续修改标题。")


@on_command('pause', aliases=('save',), only_to_me=False)
async def pause(session: CommandSession):
    await must_prepare_context(session)
    room: Room = session.get('room')
    campaign: Campaign = session.get('campaign')
    episode = await episode_ctl.get_room_running_episode(room)
    if not episode:
        session.finish('❌ 章节已经结束了哦。')
    await episode_ctl.pause_episode(episode)
    await session.send('—— 💾 保存进度 💾 ——')


async def must_prepare_context(session: CommandSession):
    if not session.is_first_run:
        return
    if session.event.detail_type != 'group':
        session.finish('🚫 这个指令只能在群聊中使用。')
    if session.event.anonymous is not None:
        session.finish('🚫 这个指令不能在匿名状态下使用。')
    room_external_id = str(session.event.group_id)
    member_external_id = str(session.event.user_id)
    room = await room_ctl.get_room_by_external(ExternalType.QQ, room_external_id)
    if not room:
        session.finish('⛔ 看起来这个群聊还没有绑定房间。\n'
                       '请在网站上创建房间并绑定该群聊后再试试吧。')
    member = await member_ctl.get_member_by_external(ExternalType.QQ, member_external_id)
    campaign = await campaign_ctl.get_campaign(room.current_campaign_id)
    if not campaign:
        session.finish('⛔ 房间内还没有已就绪的战役。\n'
                       '请在网站上创建一个战役，或是将一个已有的战役设为「当前战役」后再试试。')
    if not member or member.id != campaign.owner_id:
        session.finish('⛔ 没有权限使用该指令哦！')

    session.state['room'] = room
    session.state['member'] = member
    session.state['campaign'] = campaign
