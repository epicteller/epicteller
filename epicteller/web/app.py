#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import FastAPI

from epicteller.core import redis
from epicteller.web import bus_init
from epicteller.web.handler import auth, member, combat

app = FastAPI()


@app.on_event('startup')
async def startup():
    await redis.pool.init()
    await bus_init()

app.include_router(combat.router, prefix='/combats')
app.include_router(member.router)
app.include_router(auth.router, prefix='/auth')
