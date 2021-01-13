#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

from epicteller.core.model.combat import CombatToken
from epicteller.core.model.kafka_msg.base import KafkaMsg


class MsgCombat(KafkaMsg):
    combat_id: int


class MsgCombatCreate(MsgCombat):
    action = 'epicteller.combat.create'


class MsgCombatRun(MsgCombat):
    action = 'epicteller.combat.run'


class MsgCombatEnd(MsgCombat):
    action = 'epicteller.combat.end'


class MsgCombatActingTokenChange(MsgCombat):
    action = 'epicteller.combat.acting_token_change'
    last_token_name: str
    current_token_name: str
    rank: int
    round_count: int
    is_next_round: bool = False


class MsgCombatReorderToken(MsgCombat):
    action = 'epicteller.combat.reorder_token'
    last_order_list: List[str]
    current_order_list: List[str]


class MsgAddCombatToken(MsgCombat):
    action = 'epicteller.combat.add_combat_token'
    token: CombatToken
    rank: int


class MsgRemoveCombatToken(MsgCombat):
    action = 'epicteller.combat.remove_combat_token'
    token: CombatToken
