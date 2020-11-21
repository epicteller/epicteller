#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import FastAPI

from epicteller.web.handler import auth

app = FastAPI()

app.include_router(auth.router, prefix='/auth')
