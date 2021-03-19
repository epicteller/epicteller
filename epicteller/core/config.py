#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import os
import random


class Config:
    DEBUG = bool(os.getenv('DEBUG'))

    APP_NAME = os.environ.get('APP_NAME') or 'epicteller'

    if os.environ.get('SECRET_KEY'):
        secret = os.getenv('SECRET_KEY')
        SECRET_KEY = base64.urlsafe_b64decode(secret + '=' * (4 - len(secret) % 4))
    else:
        SECRET_KEY = b'SECRET_KEY_ENV_VAR_NOT_SET'
        print('SECRET KEY ENV VAR NOT SET! SHOULD NOT SEE IN PRODUCTION')

    # Analytics
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID')
    SEGMENT_API_KEY = os.environ.get('SEGMENT_API_KEY')

    # Sentry
    SENTRY_DSN = os.environ.get('SENTRY_DSN')

    # MySQL
    MYSQL_URL = os.environ.get('EPICTELLER_MYSQL_URL')

    # Redis
    REDIS_URL = os.getenv('EPICTELLER_REDIS_URL')

    # Kafka
    KAFKA_SERVERS = os.getenv('EPICTELLER_KAFKA_SERVERS', '').split(',')

    # Tencent Cloud COS Keys
    COS_SECRET_ID = os.getenv('COS_SECRET_ID')
    COS_SECRET_KEY = os.getenv('COS_SECRET_KEY')
    COS_REGION = os.getenv('COS_REGION')
    COS_IMAGE_BUCKET = os.getenv('COS_IMAGE_BUCKET')

    REQUEST_TIMEOUT = 600
    RESPONSE_TIMEOUT = 600

    RUNTIME_ID = f'{random.randint(0, 9999):04d}'
    HOSTNAME = os.getenv('HOSTNAME')

    ACCESS_TOKEN_LIFETIME = 30 * 86400

    SENDCLOUD_API_USER = os.getenv('SENDCLOUD_API_USER')
    SENDCLOUD_API_KEY = os.getenv('SENDCLOUD_API_KEY')
