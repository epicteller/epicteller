#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import httpx

from epicteller.core.config import Config


async def send_register_email(email: str, token: str):
    body = {
        'apiUser': Config.SENDCLOUD_API_USER,
        'apiKey': Config.SENDCLOUD_API_KEY,
        'from': 'mailgun@epicteller.com',
        'fromName': 'Epicteller邮件验证',
        'templateInvokeName': 'epicteller_register',
        'xsmtpapi': json.dumps({
            'to': [email],
            'sub': {'%token%': [token]},
        }),
    }
    async with httpx.AsyncClient() as http_client:
        r = await http_client.post(
            'https://api.sendcloud.net/apiv2/mail/sendtemplate',
            data=body,
        )
        r.raise_for_status()
