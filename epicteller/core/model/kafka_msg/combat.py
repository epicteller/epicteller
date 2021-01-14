#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

from epicteller.core.model.combat import CombatToken
from epicteller.core.model.kafka_msg import base
from epicteller.core.model.kafka_msg.base import KafkaMsg


class MsgCombat(KafkaMsg):
    combat_id: int


@base.action('epicteller.combat.create')
class MsgCombatCreate(MsgCombat):
    pass


@base.action('epicteller.combat.run')
class MsgCombatRun(MsgCombat):
    pass


@base.action('epicteller.combat.end')
class MsgCombatEnd(MsgCombat):
    pass


@base.action('epicteller.combat.acting_token_change')
class MsgCombatActingTokenChange(MsgCombat):
    last_token_name: str
    current_token_name: str
    rank: int
    round_count: int
    is_next_round: bool = False


@base.action('epicteller.combat.reorder_token')
class MsgCombatReorderToken(MsgCombat):
    last_order_list: List[str]
    current_order_list: List[str]


@base.action('epicteller.combat.add_combat_token')
class MsgAddCombatToken(MsgCombat):
    token: CombatToken
    rank: int


@base.action('epicteller.combat.remove_combat_token')
class MsgRemoveCombatToken(MsgCombat):
    token: CombatToken
