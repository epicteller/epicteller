#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sanic import Sanic, response
from sanic_auth import Auth
from sanic_session import Session, AIORedisSessionInterface

from epicteller.core.redis import redis
from epicteller.core.config import Config
from epicteller.core.util.load_module import load_modules

_app = Sanic(__name__)
auth = Auth(_app)


def create_app():
    app = _app
    app.config.from_object(Config)

    Session(app, interface=AIORedisSessionInterface(redis=redis))

    auth.no_auth_handler(lambda request: response.text('', status=401))

    load_modules('epicteller.web.handler', recursive=True)

    return app


def route(url: str):
    def decorate(handler):
        _app.add_route(handler.as_view(), url)
        return handler
    return decorate


def websocket_route(url: str):
    def decorate(handler):
        _app.add_websocket_route(handler.as_view(), url)
        return handler
    return decorate
