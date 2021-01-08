#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import functools
import time
from collections import defaultdict
from typing import List, Callable, Union, Awaitable

import sentry_sdk
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from epicteller.core.log import logger
from epicteller.core.util.load_module import load_modules


class Bus:

    def __init__(self, bootstrap_servers: Union[str, List[str]],
                 loop=asyncio.get_event_loop(),
                 job_paths: List[str] = None,
                 *args, **kwargs):
        if job_paths is None:
            job_paths = []
        self.bootstrap_servers = bootstrap_servers
        self.loop = loop
        self.init_args = args
        self.init_kwargs = kwargs
        self.job_paths = job_paths
        self._subscribers = defaultdict(set)
        self.consumer = None
        self.producer = None

    def attach(self, topic: str, subscriber: Callable) -> None:
        self._subscribers[topic].add(subscriber)
        if self.consumer:
            self.consumer.subscribe(self.topics)

    def detach(self, topic: str, subscriber: Callable) -> None:
        self._subscribers[topic].discard(subscriber)
        if not self._subscribers[topic]:
            del self._subscribers[topic]
        if self.consumer:
            self.consumer.subscribe(self.topics)

    @property
    def topics(self) -> List[str]:
        return list(self._subscribers.keys())

    @staticmethod
    async def _execute(subscriber: Callable[[str, str], Awaitable], topic: str, data: str):
        try:
            await subscriber(topic, data)
        except Exception as e:
            logger.error(f"Bot actor error when running topic [{topic}]: {e}")
            sentry_sdk.capture_exception(e)

    def dispatch(self, topic: str, data: str) -> None:
        for subscriber in self._subscribers[topic]:
            asyncio.create_task(self._execute(subscriber, topic, data))

    def on(self, topics: List[str]):
        """
        根据函数构建订阅者，并注册到对应的 topic 下
        """
        if type(topics) not in [list, tuple, set]:
            topics = [topics]

        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            for topic in topics:
                self.attach(topic, wrapper)
            return wrapper

        return decorator

    async def run(self) -> None:
        for path in self.job_paths:
            load_modules(path, recursive=True)
        try:
            self.consumer = AIOKafkaConsumer(loop=self.loop,
                                             bootstrap_servers=self.bootstrap_servers,
                                             *self.init_args,
                                             **self.init_kwargs)
            self.consumer.subscribe(self.topics)
            await self.consumer.start()
        except Exception:
            self.loop.stop()
            raise
        try:
            # Consume messages
            async for msg in self.consumer:
                print(
                    f'received: {msg.topic}, {msg.offset}, {msg.key}, {msg.value}, {time.time() - msg.timestamp / 1000}')
                self.dispatch(msg.topic, msg.value)
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await self.consumer.stop()

    async def send(self, topic: str, data: str):
        if not self.producer:
            self.producer = AIOKafkaProducer(loop=self.loop,
                                             bootstrap_servers=self.bootstrap_servers,
                                             *self.init_args,
                                             **self.init_kwargs)
            await self.producer.start()
        await self.producer.send_and_wait(topic, data.encode('utf8'))
