#!/usr/bin/env python
# -*- coding: utf-8 -*-
from email_validator import validate_email, EmailNotValidError


def is_qq_number_email(email_str: str):
    try:
        email = validate_email(email_str, check_deliverability=False)
    except EmailNotValidError:
        return False
    assert isinstance(email.local_part, str)
    return email.local_part.isdigit() and email.domain == 'qq.com'
