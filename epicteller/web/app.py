#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.authentication import AuthenticationMiddleware

from epicteller.core import redis
from epicteller.core.config import Config
from epicteller.core.error.base import EpictellerError
from epicteller.web import bus_init
from epicteller.web.handler import auth, me, combat, episode, campaign, room, misc, character
from epicteller.web.middleware.auth import AuthBackend

app = FastAPI()

cors_options = dict(
    allow_origin_regex=r'.*' if Config.DEBUG else r'https?://.*\.epicteller\.com',
    allow_origins='*' if Config.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CORSMiddleware, **cors_options)
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

root_router = APIRouter()


@root_router.get('/')
async def hello():
    return {'message': 'Hello!'}


routers = [
    root_router,
    campaign.router,
    character.router,
    combat.router,
    me.router,
    misc.router,
    auth.router,
    episode.router,
    room.router,
]

for router in routers:
    app.include_router(router)
    app.include_router(router, prefix='/api')
