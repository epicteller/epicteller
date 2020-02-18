#!/usr/bin/env python
# -*- coding: utf-8 -*-

from epicteller.core.config import Config
from epicteller.core.mysql import Tables


table = Tables(user=Config.MYSQL_USERNAME, password=Config.MYSQL_PASSWORD,
               host=Config.MYSQL_HOST, port=int(Config.MYSQL_PORT), database=Config.MYSQL_DATABASE)
