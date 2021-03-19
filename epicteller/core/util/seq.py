#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import random
import time


class IdWorker(object):
    def __init__(self, worker_id, host_id):
        self.worker_id = worker_id
        self.host_id = host_id

        self.logger = logging.getLogger("idworker")

        # stats
        self.ids_generated = 0

        # Since epicteller start.
        self.twepoch = 1577808000000

        self.sequence = 0
        self.worker_id_bits = 8
        self.data_center_id_bits = 2
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_data_center_id = -1 ^ (-1 << self.data_center_id_bits)
        self.sequence_bits = 12

        self.worker_id_shift = self.sequence_bits
        self.data_center_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = self.sequence_bits + self.worker_id_bits + self.data_center_id_bits
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)

        self.last_timestamp = -1

        # Sanity check for worker_id
        if self.worker_id > self.max_worker_id or self.worker_id < 0:
            raise Exception("worker_id", "worker id can't be greater than %i or less than 0" % self.max_worker_id)

        if self.host_id > self.max_data_center_id or self.host_id < 0:
            raise Exception("host_id", "data center id can't be greater than %i or less than 0" % self.max_data_center_id)

        self.logger.info("worker starting. timestamp left shift %d, data center id bits %d, worker id bits %d, sequence bits %d, worker id %d" % (self.timestamp_left_shift, self.data_center_id_bits, self.worker_id_bits, self.sequence_bits, self.worker_id))

    def _time_gen(self):
        return int(time.time() * 1000)

    def _till_next_millis(self, last_timestamp):
        timestamp = self._time_gen()
        while timestamp <= last_timestamp:
            timestamp = self._time_gen()

        return timestamp

    def _next_id(self, timestamp):

        if self.last_timestamp > timestamp:
            self.logger.warning("clock is moving backwards. Rejecting request until %i" % self.last_timestamp)
            raise Exception("Clock moved backwards. Refusing to generate id for %i milliseocnds" % self.last_timestamp)

        if self.last_timestamp == timestamp:
            self.sequence = (self.sequence + 1) & self.sequence_mask
            if self.sequence == 0:
                timestamp = self._till_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        new_id = ((timestamp - self.twepoch) << self.timestamp_left_shift) | (self.host_id << self.data_center_id_shift) | (self.worker_id << self.worker_id_shift) | self.sequence
        self.ids_generated += 1
        return new_id

    def get_worker_id(self):
        return self.worker_id

    def get_timestamp(self):
        return self._time_gen()

    def get_id(self):
        timestamp = self._time_gen()
        new_id = self._next_id(timestamp)
        self.logger.debug("id: %i  worker_id: %i  host_id: %i" % (new_id, self.worker_id, self.host_id))
        return new_id

    def get_host_id(self):
        return self.host_id


_host_id = os.getenv('HOST_ID', random.randint(0, 3))
_worker_id = os.getenv('WORKER_ID', random.randint(0, 255))
_worker = IdWorker(_worker_id, _host_id)


def get_id() -> int:
    return _worker.get_id()
