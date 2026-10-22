import os
import sys
from concurrent.futures import ThreadPoolExecutor

# Add module path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastlib.utils.snowflake_util import snowflake_id


def test_snowflake_id_unique_across_threads():
    """Concurrent snowflake_id() calls must not raise and must not collide."""

    def take(_: int) -> list[int]:
        return [snowflake_id() for _ in range(5000)]

    with ThreadPoolExecutor(max_workers=8) as pool:
        ids = [i for chunk in pool.map(take, range(8)) for i in chunk]

    assert len(ids) == len(set(ids)) == 40000


def test_snowflake_id_increasing_in_one_thread():
    ids = [snowflake_id() for _ in range(1000)]
    assert ids == sorted(ids)
