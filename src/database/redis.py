"""Centralised Redis helper.

Provides:
* a lazily‑created singleton ``Redis`` client that re‑uses a global
  ``ConnectionPool``;
* high‑level helpers ``add_jti_to_blacklist`` and ``is_jti_blacklisted``;
* ``close_redis`` for graceful shutdown (to be called from the app lifespan).
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator

import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis

from src.core.config import database_settings as settings

log = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Global objects – created on first use
# ----------------------------------------------------------------------
_pool: ConnectionPool | None = None
_client: Redis | None = None


def _ensure_pool() -> ConnectionPool:
    """Create the connection pool the first time it is needed."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
            decode_responses=True,
            max_connections=10,
        )
        log.debug("Redis connection pool created")
    return _pool


def get_redis_client() -> Redis:
    """Return a singleton ``Redis`` client that shares the global pool."""
    global _client
    if _client is None:
        _client = redis.Redis(connection_pool=_ensure_pool())
        log.debug("Redis client instantiated")
    return _client


# ----------------------------------------------------------------------
# Context manager – kept for API compatibility (e.g. in older code)
# ----------------------------------------------------------------------
async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    Yield the singleton client.  The context manager does **not** close the
    client; it merely provides a convenient ``async with`` syntax for callers
    that expect one.
    """
    client = get_redis_client()
    try:
        yield client
    finally:
        # No per‑call close – the client lives for the whole process.
        pass


# ----------------------------------------------------------------------
# Public helper functions used throughout the codebase
# ----------------------------------------------------------------------
async def add_jti_to_blacklist(jti: str, ttl: int = 60 * 60 * 24 * 7) -> None:
    """
    Store a JWT identifier (JTI) in Redis for ``ttl`` seconds.
    """
    client = get_redis_client()
    await client.set(jti, "1", ex=ttl)


async def is_jti_blacklisted(jti: str) -> bool:
    """
    Return ``True`` if the supplied JTI exists in the blacklist.
    """
    client = get_redis_client()
    # ``exists`` returns 0 or 1 → cast to ``bool`` for clarity.
    return bool(await client.exists(jti))


# ----------------------------------------------------------------------
# Graceful shutdown helper – to be called from the FastAPI lifespan
# ----------------------------------------------------------------------
async def close_redis() -> None:
    """
    Close the singleton client and disconnect the underlying pool.
    This must be awaited during application shutdown to avoid “Event loop is
    closed” errors.
    """
    global _client, _pool

    if _client is not None:
        try:
            await _client.aclose()  # close sockets
            await _client.connection_pool.disconnect()  # release pool resources
            log.debug("Redis client closed")
        finally:
            _client = None

    if _pool is not None:
        try:
            await _pool.disconnect()
            log.debug("Redis connection pool disconnected")
        finally:
            _pool = None
