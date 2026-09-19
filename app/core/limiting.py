from fastapi import Request,HTTPException,status
from app.core.redis import RedisClient
from app.core.config import settings

def rate_limit(l:int,w:int):
    def checker(request:Request,redis:RedisClient):
        if settings.testing:
            return None
        user_host=request.client.host
        key=f'rl:{request.url.path}:{user_host}'
        current=redis.incr(key)
        if current==1:
            redis.expire(key,w)
        if current>l:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail='Too many requests'
            )
    return checker