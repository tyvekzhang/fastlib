"""
Snowflake utils to generate unique id
"""

import os
import time
import threading
from typing import Generator


API_EPOCH = 1730438845000

worker_id_bits = 5
process_id_bits = 5
sequence_bits = 12

max_worker_id = (1 << worker_id_bits) - 1
max_process_id = (1 << process_id_bits) - 1
sequence_mask = (1 << sequence_bits) - 1

worker_id_shift = sequence_bits
process_id_shift = sequence_bits + worker_id_bits
timestamp_left_shift = sequence_bits + worker_id_bits + process_id_bits


# =========================
# Snowflake Generator
# =========================

def generator(
    worker_id: int = 1,
    process_id: int = os.getpid() & max_process_id,
) -> Generator[int, None, None]:
    """
    Generates unique snowflake IDs.
    """
    assert 0 <= worker_id <= max_worker_id
    assert 0 <= process_id <= max_process_id

    last_timestamp = -1
    sequence = 0
    lock = threading.Lock()

    def current_millis():
        return int(time.time() * 1000)

    def wait_next_millis(ts):
        while True:
            now = current_millis()
            if now > ts:
                return now

    while True:
        with lock:
            timestamp = current_millis()

            if timestamp < last_timestamp:
                raise RuntimeError("Clock moved backwards")

            if timestamp == last_timestamp:
                sequence = (sequence + 1) & sequence_mask
                if sequence == 0:
                    timestamp = wait_next_millis(timestamp)
            else:
                sequence = 0

            last_timestamp = timestamp

            yield (
                ((timestamp - API_EPOCH) << timestamp_left_shift)
                | (process_id << process_id_shift)
                | (worker_id << worker_id_shift)
                | sequence
            )


global_generator = generator()


def snowflake_id() -> int:
    """
    Returns a unique snowflake ID.
    """
    return next(global_generator)
