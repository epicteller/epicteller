#!/usr/bin/env python
# -*- coding: utf-8 -*-

from epicteller.core.controller import character as character_ctl
from epicteller.core.controller import member as member_ctl


async def bind_member_character(member_id: int):
    member = await member_ctl.get_member(member_id)
    member_externals = await member_ctl.get_member_externals(member_id)
    for external_type, external_id in member_externals.items():
        characters = await character_ctl.get_characters_by_external(external_type, external_id)
        for character in characters:
            if character.member_id != 0:
                continue
            await character_ctl.bind_character_member(character, member)
