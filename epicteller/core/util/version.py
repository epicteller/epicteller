#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
from os.path import dirname

import git

import epicteller


@functools.lru_cache()
def get_commit() -> str:
    try:
        return git.Repo(dirname(dirname(epicteller.__file__))).git.describe(always=True, tags=True, dirty=True)
    except:
        return 'unknown'
