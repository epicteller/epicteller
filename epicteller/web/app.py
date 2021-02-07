#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.authentication import AuthenticationMiddleware

from epicteller.core import redis
from epicteller.core.config import Config
from epicteller.core.error.base import EpictellerError
from epicteller.web import bus_init
from epicteller.web.handler import auth, me, combat
from epicteller.web.middleware.auth import AuthBackend

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


@app.exception_handler(EpictellerError)
async def _(request: Request, e: EpictellerError):
    return JSONResponse(
        status_code=e.status_code,
        content={
            'message': e.message,
            'code': e.code,
            'name': e.name,
            'detail': e.detail,
        },
    )


@app.exception_handler(ValidationError)
async def _(request: Request, e: ValidationError):
    return JSONResponse(
        status_code=400,
        content={
            'message': 'ValidationError',
            'name': 'ValidationError',
            'code': 4000,
            'detail': e.errors(),
        },
    )


@app.get('/')
async def hello():
    return {'message': 'Hello!'}

app.include_router(combat.router, prefix='/combats')
app.include_router(me.router, prefix='/me')
app.include_router(auth.router, prefix='/auth')

