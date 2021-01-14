#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

from epicteller.core.model.combat import CombatToken
from epicteller.core.model.kafka_msg import base
from epicteller.core.model.kafka_msg.base import KafkaMsg


class MsgCombat(KafkaMsg):
    combat_id: int


@base.action
class MsgCombatCreate(MsgCombat):
    action = 'epicteller.combat.create'


@base.action
class MsgCombatRun(MsgCombat):
    action = 'epicteller.combat.run'


@base.action
class MsgCombatEnd(MsgCombat):
    action = 'epicteller.combat.end'


@base.action
class MsgCombatActingTokenChange(MsgCombat):
    action = 'epicteller.combat.acting_token_change'
    last_token_name: str
    current_token_name: str
    rank: int
    round_count: int
    is_next_round: bool = False


@base.action
class MsgCombatReorderToken(MsgCombat):
    action = 'epicteller.combat.reorder_token'
    last_order_list: List[str]
    current_order_list: List[str]


@base.action
class MsgAddCombatToken(MsgCombat):
    action = 'epicteller.combat.add_combat_token'
    token: CombatToken
    rank: int


@base.action
class MsgRemoveCombatToken(MsgCombat):
    action = 'epicteller.combat.remove_combat_token'
    token: CombatToken
