#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import httpx

from epicteller.core.config import Config
from epicteller.core.log import logger


async def send_email(email: str, title: str, content: str, link: str):
    body = {
        'apiUser': Config.SENDCLOUD_API_USER,
        'apiKey': Config.SENDCLOUD_API_KEY,
        'from': 'mailgun@epicteller.com',
        'fromName': 'Epicteller「邮件姬」',
        'templateInvokeName': 'epicteller_register',
        'xsmtpapi': json.dumps({
            'to': [email],
            'sub': {
                '%title%': [title],
                '%content%': [content],
                '%link%': [link],
            },
        }),
    }
    async with httpx.AsyncClient() as http_client:
        r = await http_client.post(
            'https://api.sendcloud.net/apiv2/mail/sendtemplate',
            data=body,
        )
        r.raise_for_status()


async def send_register_email(email: str, token: str):
    link = f'https://www.epicteller.com/register?token={token}'
    await send_email(email,
                     '注册帐号',
                     '你好！你可以通过以下链接来注册 Epicteller 帐号:',
                     link)


async def send_reset_email(email: str, token: str):
    link = f'https://www.epicteller.com/reset-password?token={token}'
    await send_email(email,
                     '重置密码',
                     '你好！你可以通过以下链接来重置你帐号的密码:',
                     link)


async def send_bind_external_email(email: str, token: str):
    await send_email(email,
                     '绑定外部帐号',
                     '你好！请输入下方的验证码来绑定外部帐号。如果你不知道这封邮件为什么会发送给你，请简单地忽略该邮件：',
                     f'<h2>{token}</h2>')
