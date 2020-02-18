#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quart import Quart

from epicteller.core.config import Config


def create_app():
    app = Quart(__name__)
    app.config.from_object(Config)

    return app
