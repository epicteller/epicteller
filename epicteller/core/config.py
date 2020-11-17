#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random


class Config:
    APP_NAME = os.environ.get('APP_NAME') or 'epicteller'

    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'SECRET_KEY_ENV_VAR_NOT_SET'
        print('SECRET KEY ENV VAR NOT SET! SHOULD NOT SEE IN PRODUCTION')

    # Analytics
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID')
    SEGMENT_API_KEY = os.environ.get('SEGMENT_API_KEY')

    # Sentry
    SENTRY_API_KEY = os.environ.get('SENTRY_API_KEY')

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
