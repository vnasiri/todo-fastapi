import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import redis as redis_helper
from src.database.db import get_session
from src.entities.todo import Todo
from src.entities.user import User
from src.main import app
from src.tests.example import create_test_user
from src.tests.utils.auth import issue_test_token

# ----------------------------------------------------------------------
# 1. In‑memory SQLite for tests
# ----------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:?cache=shared"

engine = create_async_engine(
    TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)

async_test_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------
# 2. Create / drop tables for each test function
# ---------------------
@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_database():
    """Clean slate for every test ensures data isolation."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


# ------------------------
# 3. Direct DB session (optional, for tests that need it)
# ------------------------
@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_test_session_maker() as session:
        yield session


# -------------------------
# 4. Redis cleanup – ensure the singleton client/pool is torn down
# -------------------------
@pytest_asyncio.fixture(scope="function", autouse=True)
async def redis_cleanup():
    """
    After each test we close the global Redis client/pool.
    This mirrors the production shutdown hook and guarantees test isolation.
    """
    # After each test, ensure the client is closed
    yield
    try:
        await redis_helper.close_redis()
    except Exception as exc:
        # Log but don’t crash the entire suite
        print(f"Redis cleanup failed: {exc}")


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession, test_user: User
) -> AsyncGenerator[AsyncClient, None]:
    """Builds a client with dependency overrides."""

    async def get_session_override():
        yield db_session

    async def fake_is_jti_blacklisted(_: str) -> bool:
        return False

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[redis_helper.is_jti_blacklisted] = fake_is_jti_blacklisted

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# -------------------------
# 6. Auth fixtures
# -------------------------
@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Best Practice: Create user and token in one step for clean test state."""
    return await create_test_user(db_session)


@pytest_asyncio.fixture(scope="function")
async def auth_headers(test_user: User) -> dict[str, str]:
    print(test_user)
    token = await issue_test_token(test_user)
    return {"Authorization": f"Bearer {token}"}
