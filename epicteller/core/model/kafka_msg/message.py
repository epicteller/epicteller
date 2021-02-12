#!/usr/bin/env python
# -*- coding: utf-8 -*-
from epicteller.core.model.kafka_msg import base
from epicteller.core.model.kafka_msg.base import KafkaMsg
from epicteller.core.model.message import MessageContent
from epicteller.core.util.enum import MessageType


class MsgMessage(KafkaMsg):
    action = 'epicteller.message'
    message_id: int


@base.action
class MsgMessageCreate(MsgMessage):
    action = 'epicteller.message.create'
    episode_id: int
    character_id: int
    is_gm: bool
    content: MessageContent
    type: MessageType
    created: int
    updated: int


@base.action
class MsgMessageRemove(MsgMessage):
    action = 'epicteller.message.remove'


@base.action
class MsgMessageRecover(MsgMessage):
    action = 'epicteller.message.recover'


@base.action
class MsgMessageEdit(MsgMessage):
    action = 'epicteller.message.edit'
    content: MessageContent
