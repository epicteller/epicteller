#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sanic import response
from sanic.request import Request
from sanic.views import HTTPMethodView

from epicteller.core.controller import message as message_ctl
from epicteller.web import app


@app.route('/episodes/<episode_id:int>/messages')
class EpisodeMessagesHandler(HTTPMethodView):
    async def get(self, request: Request, episode_id: int):
        oldest = request.args.get('oldest')
        latest = request.args.get('latest')
        if oldest and oldest != '0':
            oldest = await message_ctl.get_message(url_token=oldest)
            oldest = oldest.id if oldest else None
        elif oldest and oldest == '0':
            oldest = 0
        elif latest:
            latest = await message_ctl.get_message(url_token=latest)
            latest = latest.id if latest else None
        limit = request.args.get('limit', 20)
        messages = await message_ctl.get_episode_messages(episode_id, oldest=oldest, latest=latest, limit=limit)
        return response.json(messages)
