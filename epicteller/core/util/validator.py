#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from email_validator import validate_email, EmailNotValidError


def parse_external_id_from_qq_email(email_str: str) -> Optional[str]:
    try:
        email = validate_email(email_str, check_deliverability=False)
    except EmailNotValidError:
        return
    assert isinstance(email.local_part, str)
    if email.local_part.isdigit() and email.domain == 'qq.com':
        return email.local_part
