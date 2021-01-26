#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware

from epicteller.core import redis
from epicteller.core.config import Config
from epicteller.web import bus_init
from epicteller.web.handler import auth, member, combat

app = FastAPI()


allow_origins = ['*']
if Config.DEBUG:
    allow_origins.append("*")

app.add_middleware(CORSMiddleware,
                   allow_origins=allow_origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])
app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())


@app.on_event('startup')
async def startup():
    bus_init()
    await redis.pool.init()


@app.get('/')
async def hello():
    return {'message': 'Hello!'}

app.include_router(combat.router, prefix='/combats')
app.include_router(member.router)
app.include_router(auth.router, prefix='/auth')

