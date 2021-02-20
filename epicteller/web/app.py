#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.authentication import AuthenticationMiddleware

from epicteller.core import redis
from epicteller.core.config import Config
from epicteller.core.error.base import EpictellerError
from epicteller.web import bus_init
from epicteller.web.handler import auth, me, combat, episode, campaign, room, misc
from epicteller.web.middleware.auth import AuthBackend

app = FastAPI()


origin_regex = r'https?://.*\.epicteller\.com'
if Config.DEBUG:
    origin_regex = r'.*'

app.add_middleware(CORSMiddleware,
                   allow_origin_regex=origin_regex,
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


async def validation_error_handler(request: Request, e: ValidationError):
    return JSONResponse(
        status_code=400,
        content={
            'message': '数据格式非法',
            'name': 'ValidationError',
            'code': 4000,
            'detail': e.errors(),
        },
    )

app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)


@app.get('/')
async def hello():
    return {'message': 'Hello!'}

app.include_router(campaign.router)
app.include_router(combat.router)
app.include_router(me.router)
app.include_router(misc.router)
app.include_router(auth.router)
app.include_router(episode.router)
app.include_router(room.router)

