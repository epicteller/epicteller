#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


class Config:
    APP_NAME = os.environ.get('APP_NAME') or 'epicteller'

    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'SECRET_KEY_ENV_VAR_NOT_SET'
        print('SECRET KEY ENV VAR NOT SET! SHOULD NOT SEE IN PRODUCTION')

        # Analytics
        GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID') or ''
        SEGMENT_API_KEY = os.environ.get('SEGMENT_API_KEY') or ''

        # Sentry
        SENTRY_API_KEY = os.environ.get('SENTRY_API_KEY')

        # MySQL
        MYSQL_USERNAME = os.environ.get('EPICTELLER_MYSQL_USERNAME')
        MYSQL_PASSWORD = os.environ.get('EPICTELLER_MYSQL_PASSWORD')
        MYSQL_HOST = os.environ.get('EPICTELLER_MYSQL_HOST')
        MYSQL_PORT = os.environ.get('EPICTELLER_MYSQL_PORT')
        MYSQL_DATABASE = os.environ.get('EPICTELLER_MYSQL_DATABASE')

        # Redis
        REDIS_URL = os.getenv('REDIS_URL') or 'http://localhost:6379'
