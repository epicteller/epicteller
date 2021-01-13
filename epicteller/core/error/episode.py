#!/usr/bin/env python
# -*- coding: utf-8 -*-
from starlette.status import HTTP_404_NOT_FOUND

from epicteller.core.error.base import EpictellerError


class EpisodeError(EpictellerError):
    code = 20000


class EpisodeNotFoundError(EpisodeError):
    status_code = HTTP_404_NOT_FOUND
    code = 20001


class EpisodeRunningError(EpisodeError):
    code = 20002


class EpisodeEndedError(EpisodeError):
    code = 20003
