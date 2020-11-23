#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Dict, Union, Iterable

import bcrypt

from epicteller.core.dao.member import MemberDAO, MemberExternalDAO
from epicteller.core.model.member import Member
from epicteller.core.util.enum import ExternalType


def _gen_passhash(password: str) -> str:
    passhash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(rounds=10)).decode('utf8')
    return passhash


async def get_member(member_id: Optional[int]=None, *,
                     url_token: Optional[str]=None,
                     email: Optional[str]=None) -> Optional[Member]:
    if member_id:
        return (await MemberDAO.batch_get_member_by_id([member_id])).get(member_id)
    elif url_token:
        return (await MemberDAO.batch_get_member_by_url_token([url_token])).get(url_token)
    elif email:
        return await MemberDAO.get_member_by_email(email)
    return None


async def batch_get_member(member_ids: Iterable[int]=None, *,
                           url_tokens: Iterable[str]=None) -> Dict[Union[int, str], Member]:
    if member_ids:
        return await MemberDAO.batch_get_member_by_id(member_ids)
    elif url_tokens:
        return await MemberDAO.batch_get_member_by_url_token(url_tokens)
    return {}


async def check_member_email_password(email: str, password: str) -> Optional[Member]:
    email = email.lower()
    member = await get_member(email=email)
    if not member:
        return
    matched = bcrypt.checkpw(password.encode('utf8'), member.passhash.encode('utf8'))
    if not matched:
        return
    return member


async def create_member(name: str, email: str, password: str) -> Member:
    passhash = _gen_passhash(password)
    email = email.lower()
    return await MemberDAO.create_member(name, email, passhash)


async def bind_member_external_id(member_id: int, external_type: ExternalType, external_id: str) -> None:
    await MemberExternalDAO.bind_member_external_id(member_id, external_type, external_id)


async def unbind_member_external_id(member_id: int, external_type: ExternalType) -> None:
    await MemberExternalDAO.unbind_member_external_id(member_id, external_type)


async def get_member_externals(member_id: int) -> Dict[ExternalType, str]:
    return await MemberExternalDAO.get_external_ids_by_member(member_id)


async def get_member_by_external(external_type: ExternalType, external_id: str) -> Optional[Member]:
    member_id = await MemberExternalDAO.get_member_id_by_external(external_type, external_id)
    if not member_id:
        return None
    return await get_member(member_id)


