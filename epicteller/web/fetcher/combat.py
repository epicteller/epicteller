#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict, Optional

from epicteller.core.model.combat import Combat as CoreCombat
from epicteller.web.model.combat import Combat as WebCombat


async def fetch_combat(combat: CoreCombat) -> Optional[WebCombat]:
    if not combat:
        return
    return (await batch_fetch_combats({combat.id: combat})).get(combat.url_token)


async def batch_fetch_combats(combats: Dict[int, CoreCombat]) -> Dict[str, WebCombat]:

