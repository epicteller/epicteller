#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from epicteller.core import redis
from epicteller.web import bus_init
from epicteller.web.handler import auth, member, combat

app = FastAPI()


@app.on_event('startup')
async def startup():
    bus_init()
    await redis.pool.init()

app.include_router(combat.router, prefix='/combats')
app.include_router(member.router)
app.include_router(auth.router, prefix='/auth')

app.add_middleware(CORSMiddleware,
                   allow_origins=["http://localhost",
                                  "https://*.epicteller.com"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])
