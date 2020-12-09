#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uvicorn
from fastapi import FastAPI

from epicteller.core import redis
from epicteller.web.handler import auth, member

app = FastAPI()


@app.on_event('startup')
async def startup():
    await redis.pool.init()

app.include_router(member.router)
app.include_router(auth.router, prefix='/auth')

if __name__ == '__main__':
    uvicorn.run('epicteller.web.main:app', host='0.0.0.0')
