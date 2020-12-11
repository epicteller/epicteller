#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pydantic import BaseModel


class BasicResponse(BaseModel):
    success: bool = True
