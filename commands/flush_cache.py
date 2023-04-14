import os
import redis  # type:ignore

"""
    Initializes the database. If a database already exists, it may be dropped and recreated, so that it can be rebuild cleanly.
"""

EXPECTED_REDIS_CONTAINER_NAME = "redis"


def run() -> None:
    client = redis.Redis(  # type:ignore
        host=f"cache.{os.environ.get('HOST','localhost')}", port="6379", password=f"{os.environ.get('REDIS_PASS','redis_pass')}"
    )

    client.flushall()
