#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
from typing import Optional, List

from fastapi import APIRouter, WebSocket
from pydantic import BaseModel, validator

from epicteller.core.controller import character as character_ctl
from epicteller.core.controller import combat as combat_ctl
from epicteller.core.model.combat import Combat, CombatToken
from epicteller.core.error.base import NotFoundError
from epicteller.core.model.kafka_msg.base import get_msg_model
from epicteller.core.model.kafka_msg.combat import MsgCombat
from epicteller.web import bus
from epicteller.web.fetcher import combat as combat_fetcher
from epicteller.web.model.combat import Combat as WebCombat
from epicteller.web.model.combat import CombatToken as WebCombatToken

router = APIRouter()


async def must_prepare_combat(url_token: str) -> Combat:
    combat = await combat_ctl.get_combat(url_token=url_token)
    if not combat:
        raise NotFoundError()
    return combat


@router.get('/{url_token}', response_model=WebCombat, response_model_exclude_none=True)
async def get_combat(url_token: str):
    combat = await must_prepare_combat(url_token=url_token)
    web_combat = await combat_fetcher.fetch_combat(combat)
    return web_combat


class CombatLiveMsg(BaseModel):
    combat: WebCombat
    action: MsgCombat


@router.websocket('/{url_token}')
async def combat_live(websocket: WebSocket, url_token: str):
    combat = await must_prepare_combat(url_token)
    await websocket.accept()

    topics = [
        'epicteller.combat.run',
        'epicteller.combat.end',
        'epicteller.combat.acting_token_change',
        'epicteller.combat.reorder_token',
        'epicteller.combat.add_combat_token',
        'epicteller.combat.remove_combat_token',
    ]

    async def actor(event: str, data: bytes):
        model_cls = get_msg_model(event)
        msg = model_cls.parse_raw(data)
        assert isinstance(msg, MsgCombat)
        if msg.combat_id != combat.id:
            return
        new_combat = await combat_ctl.get_combat(combat.id)
        out_msg = CombatLiveMsg(
            combat=await combat_fetcher.fetch_combat(new_combat),
            action=msg,
        )
        out_data = out_msg.dict(exclude={'action': {'combat_id'}}, skip_defaults=None)
        await websocket.send_json(out_data)

    try:
        bus.attach(topics, actor)
        while True:
            _ = await websocket.receive()
    finally:
        bus.detach(topics, actor)


class UpdateCombatArgs(BaseModel):
    class UpdateAction(Enum):
        RUN = 'run'
        END = 'end'
        NEXT = 'next'
        REORDER = 'reorder'
    action: UpdateAction

    tokens: Optional[List[str]]

    @validator('tokens', always=True)
    def must_have_reorder_tokens(cls, tokens: Optional[List[str]], values: dict):
        if values['action'] == cls.UpdateAction.REORDER:
            assert tokens
        return tokens


@router.put('/{url_token}', response_model=WebCombat, response_model_exclude_none=True)
async def update_combat(url_token: str, args: UpdateCombatArgs):
    combat = await must_prepare_combat(url_token)
    if args.action == UpdateCombatArgs.UpdateAction.RUN:
        await combat_ctl.run_combat(combat)
    elif args.action == UpdateCombatArgs.UpdateAction.END:
        await combat_ctl.end_combat(combat)
    elif args.action == UpdateCombatArgs.UpdateAction.NEXT:
        await combat_ctl.next_combat_token(combat)
    elif args.action == UpdateCombatArgs.UpdateAction.REORDER:
        await combat_ctl.reorder_tokens(combat, args.tokens)
    return await combat_fetcher.fetch_combat(combat)


class CombatTokenIn(BaseModel):
    name: str
    initiative: float = 0
    character_id: Optional[str]


class CombatTokenOut(BaseModel):
    token: WebCombatToken
    rank: int


@router.post('/{url_token}/tokens', response_model=CombatTokenOut, response_model_exclude_none=True)
async def add_combat_token(url_token: str, token_in: CombatTokenIn):
    combat = await must_prepare_combat(url_token)
    character_id: Optional[int] = None
    if token_in.character_id:
        character = await character_ctl.get_character(url_token=token_in.character_id)
        if not character:
            raise NotFoundError()
        character_id = character.id
    token = CombatToken(name=token_in.name, initiative=token_in.initiative, character_id=character_id)
    rank = await combat_ctl.add_combat_token(combat, token)
    web_token = await combat_fetcher.fetch_combat_token(token)
    return CombatTokenOut(
        token=web_token,
        rank=rank,
    )


@router.delete('/{url_token}/tokens/{token_name}')
async def remove_combat_token(url_token: str, token_name: str):
    combat = await must_prepare_combat(url_token)
    await combat_ctl.remove_combat_token(combat, token_name)
    return {'success': True}
