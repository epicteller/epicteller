#!/usr/bin/env python
# -*- coding: utf-8 -*-
from epicteller.core.error.base import EpictellerError


class EpisodeError(EpictellerError):
    pass


class EpisodeNotFoundError(EpisodeError):
    pass


class EpisodeRunningError(EpisodeError):
    def __init__(self, episode_id: int):
        self.episode_id = episode_id


class EpisodeEndedError(EpisodeError):
    pass
