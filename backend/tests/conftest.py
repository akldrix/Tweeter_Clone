from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import fastapi as app
from app.database import get_async_session
from app.models import Base, Media, Tweet, User
from app.routes.users import get_current_user

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestSessionLocal = async_sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def init_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def db_session():
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(
    db_session: AsyncSession, test_user_1: User
) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db():
        yield db_session

    async def _override_get_current_user():
        return test_user_1

    app.dependency_overrides[get_async_session] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user_1(db_session: AsyncSession) -> User:
    user = User(name="Ivan", passkey="123")
    db_session.add(user)

    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def test_user_2(db_session: AsyncSession) -> User:
    user = User(name="Peter", passkey="234")
    db_session.add(user)

    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def test_tweet(db_session: AsyncSession, test_user_1: User) -> Tweet:
    tweet = Tweet(user_id=test_user_1.id, tweet_data="My tweet")

    db_session.add(tweet)

    await db_session.commit()
    await db_session.refresh(tweet)

    return tweet


@pytest.fixture
async def test_media(db_session: AsyncSession, test_tweet: Tweet) -> Media:
    media = Media(
        file_path="/backend/tests/test_images/test_image.png", tweet_id=test_tweet.id
    )
    db_session.add(media)

    await db_session.commit()
    await db_session.refresh(media)

    return media
