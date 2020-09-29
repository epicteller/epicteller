#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import functools
import time
from collections import defaultdict
from typing import List, Callable, Union

from aiokafka import AIOKafkaConsumer

from epicteller.core.util.load_module import load_modules


class Bus:

    def __init__(self, bootstrap_servers: Union[str, List[str]],
                 loop=asyncio.get_event_loop(),
                 job_paths: List[str] = None,
                 *args, **kwargs):
        if job_paths is None:
            job_paths = []
        self.job_paths = job_paths
        self._subscribers = defaultdict(set)
        self.consumer = AIOKafkaConsumer(loop=loop, bootstrap_servers=bootstrap_servers, *args, **kwargs)

    def attach(self, topic: str, subscriber: Callable) -> None:
        self._subscribers[topic].add(subscriber)
        self.consumer.subscribe(self.topics)

    def detach(self, topic: str, subscriber: Callable) -> None:
        self._subscribers[topic].discard(subscriber)
        if not self._subscribers[topic]:
            del self._subscribers[topic]
        self.consumer.subscribe(self.topics)

    @property
    def topics(self) -> List[str]:
        return list(self._subscribers.keys())

    def send(self, topic: str, data: str) -> None:
        for subscriber in self._subscribers[topic]:
            asyncio.create_task(subscriber(topic, data))

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
            await self.consumer.start()
        except Exception:
            asyncio.get_event_loop().stop()
            raise
        try:
            # Consume messages
            async for msg in self.consumer:
                print(
                    f'received: {msg.topic}, {msg.offset}, {msg.key}, {msg.value}, {time.time() - msg.timestamp / 1000}')
                self.send(msg.topic, msg.value)
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await self.consumer.stop()
