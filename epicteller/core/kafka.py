#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import functools
import json
from collections import defaultdict
from typing import List, Callable, Union, Awaitable, Optional, Iterable

import sentry_sdk
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from epicteller.core.config import Config
from epicteller.core.log import logger
from epicteller.core.model.kafka_msg.base import KafkaMsg
from epicteller.core.util.load_module import load_modules

_producer: Optional[AIOKafkaProducer] = None


class Bus:

    def __init__(self, bootstrap_servers: Union[str, List[str]],
                 job_paths: List[str] = None,
                 *args, **kwargs):
        if job_paths is None:
            job_paths = []
        self.bootstrap_servers = bootstrap_servers
        self.init_args = args
        self.init_kwargs = kwargs
        self.job_paths = job_paths
        self._subscribers = defaultdict(set)
        self.consumer = None
        self.producer = None

    def attach(self, topics: Union[str, Iterable[str]], subscriber: Callable) -> None:
        if isinstance(topics, str):
            topics = [topics]
        for topic in topics:
            self._subscribers[topic].add(subscriber)
        if self.consumer:
            if self.topics:
                self.consumer.subscribe(self.topics)
            else:
                self.consumer.unsubscribe()

    def detach(self, topics: Union[str, Iterable[str]], subscriber: Callable) -> None:
        if isinstance(topics, str):
            topics = [topics]
        for topic in topics:
            self._subscribers[topic].discard(subscriber)
            if not self._subscribers[topic]:
                del self._subscribers[topic]
        if self.consumer:
            if self.topics:
                self.consumer.subscribe(self.topics)
            else:
                self.consumer.unsubscribe()

    @property
    def topics(self) -> List[str]:
        return list(self._subscribers.keys())

    @staticmethod
    async def _execute(subscriber: Callable[[str, str], Awaitable], topic: str, data: str):
        try:
            await subscriber(topic, data)
        except Exception as e:
            logger.error(f"Error occurred when running topic [{topic}]: {e}")
            sentry_sdk.capture_exception(e)

    def dispatch(self, topic: str, data: str) -> None:
        for subscriber in self._subscribers[topic]:
            asyncio.create_task(self._execute(subscriber, topic, data))

    def on(self, topics: Union[List[str], str]):
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
            self.consumer = AIOKafkaConsumer(bootstrap_servers=self.bootstrap_servers,
                                             *self.init_args,
                                             **self.init_kwargs)
            if self.topics:
                self.consumer.subscribe(self.topics)
            await self.consumer.start()
        except Exception:
            raise
        try:
            # Consume messages
            async for msg in self.consumer:
                logger.debug(f'Kafka bus received topic: {msg.topic}')
                self.dispatch(msg.topic, msg.value)
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await self.consumer.stop()


async def publish(msg: KafkaMsg):
    try:
        global _producer
        if not _producer:
            _producer = AIOKafkaProducer(loop=asyncio.get_event_loop(),
                                         bootstrap_servers=Config.KAFKA_SERVERS)
            await _producer.start()
        await _producer.send_and_wait(msg.action, msg.json().encode('utf8'))
    except Exception as e:
        logger.error(f'Error occurred when publishing kafka message[{msg.action}]:', e)
