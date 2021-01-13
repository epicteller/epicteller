#!/usr/bin/env python
# -*- coding: utf-8 -*-
import itertools
from typing import Dict, Optional

from epicteller.core.controller import character as character_ctl
from epicteller.core.controller import room as room_ctl
from epicteller.core.model.combat import Combat as CoreCombat, CombatToken as CoreCombatToken
from epicteller.web.fetcher import character as character_fetcher
from epicteller.web.fetcher import room as room_fetcher
from epicteller.web.model.combat import Combat as WebCombat, CombatToken as WebCombatToken, CombatOrder


async def fetch_combat(combat: CoreCombat) -> Optional[WebCombat]:
    if not combat:
        return
    return (await batch_fetch_combats({combat.id: combat})).get(combat.id)


async def batch_fetch_combats(combats: Dict[int, CoreCombat]) -> Dict[int, WebCombat]:
    room_ids = list({c.room_id for c in combats.values()})
    rooms = await room_ctl.batch_get_room(room_ids)
    web_rooms = await room_fetcher.batch_fetch_room(rooms)
    tokens = [combat.tokens.values() for combat in combats.values()]
    tokens = list(itertools.chain(*tokens))
    character_ids = list({token.character_id for token in tokens if token.character_id})
    characters = await character_ctl.batch_get_character(character_ids)
    web_characters = await character_fetcher.batch_fetch_characters(characters)
    results = {}
    for cid, c in combats.items():
        if not c:
            continue
        web_tokens = {token.name: WebCombatToken(
            name=token.name,
            initiative=token.initiative,
            character=web_characters.get(token.character_id)
        ) for token in c.tokens.values()}
        result = WebCombat(
            id=c.url_token,
            room=web_rooms.get(c.room_id),
            state=c.state.name.lower(),
            is_removed=c.is_removed,
            tokens=web_tokens,
            order=CombatOrder(
                order=[web_tokens.get(token_name) for token_name in c.order.order_list],
                current_token=web_tokens.get(c.order.current_token_name),
                round_count=c.order.round_count,
            ),
            data=c.data,
            started_at=c.started_at,
            ended_at=c.ended_at,
            created=c.created,
            updated=c.updated,
        )
        results[cid] = result
    return results


async def fetch_combat_token(token: CoreCombatToken) -> Optional[WebCombatToken]:
    if not token:
        return
    character = await character_ctl.get_character(token.character_id)
    web_character = await character_fetcher.fetch_character(character)
    return WebCombatToken(name=token.name, initiative=token.initiative, character=web_character)
