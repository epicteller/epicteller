#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from contextlib import asynccontextmanager

import aiomysql
import asyncio
import contextvars
import json
import logging
import time

from aiomysql.sa import create_engine as async_create_engine
from sqlalchemy import create_engine, exc, MetaData
from sqlalchemy.engine.url import make_url

_g = contextvars.ContextVar('connection')
logger = logging.getLogger('db')


class DBProxy(object):

    def __init__(self, user, password, host, port, database,
                 longquery_time=1.0, minsize=1, maxsize=10,
                 pool_recycle=1800, connect_timeout=10):
        self.master = None
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.mysql_longquery_time = longquery_time
        self.minsize = minsize
        self.maxsize = maxsize
        self.pool_recycle = pool_recycle
        self.connect_timeout = connect_timeout

    async def init(self):
        if self.master:
            return
        self.master = await async_create_engine(user=self.user, password=self.password,
                                                host=self.host, port=self.port, db=self.database,
                                                charset='utf8mb4',
                                                autocommit=True,
                                                minsize=self.minsize,
                                                maxsize=self.maxsize,
                                                pool_recycle=self.pool_recycle,
                                                connect_timeout=self.connect_timeout)

    async def execute(self, statement, *multiparams, **params):
        await self.init()
        engine = self.master
        conn = _g.get(None)
        if not conn:
            conn = await engine.acquire()
        start_time = time.time()
        try:
            result = await conn.execute(statement, *multiparams, **params)

            total_time = time.time() - start_time
            if self.mysql_longquery_time is not None and float(total_time) > self.mysql_longquery_time:
                logger.info("%s/%s %s %dms" % (self.host,
                                               self.database,
                                               json.dumps(str(statement)),
                                               total_time * 1000))
            return result
        except aiomysql.OperationalError:
            logger.error("OperationalError in %s/%s", engine.url.host,
                                                      engine.url.database,
                         exc_info=1)
            raise
        except aiomysql.Error:
            raise
        finally:
            if _g.get(None) is None:
                engine.release(conn)

    @asynccontextmanager
    async def begin(self):
        conn = await self.master.acquire()
        trans = await conn.begin()
        token = None
        try:
            token = _g.set(conn)
            yield
            await trans.commit()
        except Exception:
            await trans.rollback()
            raise
        finally:
            self.master.release(conn)
            _g.reset(token)


class Tables(object):

    def __init__(self, url: str,
                 longquery_time=1.0, minsize=1, maxsize=10,
                 pool_recycle=1800, connect_timeout=10):
        self.url = url
        schema = make_url(url)
        self.user = schema.username
        self.password = schema.password
        self.host = schema.host
        self.port = schema.port
        self.database = schema.database
        self.__db = DBProxy(
            user=self.user, password=self.password,
            host=self.host, port=self.port, database=self.database,
            longquery_time=longquery_time,
            minsize=minsize,
            maxsize=maxsize,
            pool_recycle=pool_recycle,
            connect_timeout=connect_timeout,
        )
        self._initialize_meta()

    def _initialize_meta(self):
        engine = create_engine(self.url)
        self.meta = MetaData()
        self.meta.reflect(bind=engine)

    async def init(self):
        await self.__db.init()

    @property
    def db(self):
        return self.__db

    def __getattr__(self, name):
        try:
            return self.meta.tables[name]
        except KeyError:
            raise exc.NoSuchTableError(name)

    def execute(self, *args, **kwargs):
        try:
            return self.__db.execute(*args, **kwargs)
        except aiomysql.InternalError as e:
            # (1054, 'unknown column field')
            if e.args[0] == 1054:
                self._initialize_meta()
            raise
