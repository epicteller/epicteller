#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sentry_sdk
import uvicorn
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from epicteller.web.app import app as asgi_app


sentry_sdk.init()
app = SentryAsgiMiddleware(asgi_app)

if __name__ == '__main__':
    uvicorn.run('epicteller.web.main:app', host='0.0.0.0')
