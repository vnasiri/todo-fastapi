from slowapi import Limiter
from slowapi.util import get_remote_address
from redis.asyncio import Redis


limiter = Limiter(key_func=get_remote_address)


redis_client = Redis.from_url("redis://localhost:6379")
