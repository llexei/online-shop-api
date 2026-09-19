from fastapi import Depends
from redis import Redis
import redis
from typing import Annotated
from core.config import settings


def get_redis():
    client=redis.Redis.from_url(
        f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}',
        decode_responses=True
    )
    try:
        yield client
    finally:
        client.close()


RedisClient=Annotated[Redis,Depends(get_redis)]