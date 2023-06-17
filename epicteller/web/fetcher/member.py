#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Dict

from epicteller.core.controller import member as member_ctl
from epicteller.core.model.member import Member as CoreMember
from epicteller.core.util import imghosting
from epicteller.core.util.enum import ExternalType
from epicteller.web.model.member import Member as WebMember, Me, MemberExternalInfo


async def fetch_member(member: Optional[CoreMember]) -> Optional[WebMember]:
    if not member:
        return
    return (await batch_fetch_members({member.id: member})).get(member.id)


async def batch_fetch_members(members: Dict[int, CoreMember]) -> Dict[int, WebMember]:
    results = {}
    for mid, m in members.items():
        if not m:
            continue
        result = WebMember(
            id=m.url_token,
            name=m.name,
            headline=m.headline,
            avatar=imghosting.get_avatar_url(m.avatar),
            avatar_template=imghosting.get_avatar_url(m.avatar, size='{template}'),
            created=m.created,
        )
        results[mid] = result
    return results


async def fetch_me(member: Optional[CoreMember]) -> Optional[Me]:
    if not member:
        return
    externals = await member_ctl.get_member_externals(member.id)
    external_info = MemberExternalInfo(
        QQ=externals.get(ExternalType.QQ),
    )
    web_me = Me(
        id=member.url_token,
        name=member.name,
        headline=member.headline,
        avatar=imghosting.get_avatar_url(member.avatar),
        avatar_original=imghosting.get_avatar_url(member.avatar, size='r'),
        created=member.created,
        email=member.email,
        external_info=external_info,
    )
    return web_me
