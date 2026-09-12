from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.database import engine, get_async_session
from app.models import Base, Media, Tweet, User
from app.routes import medias, tweets, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.passkey == "test"))
        if not result.scalar_one_or_none():
            user = User(name="Test User", passkey="test")
            session.add(user)
            await session.commit()

        yield

        await engine.dispose()


fastapi = FastAPI(lifespan=lifespan)


@fastapi.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "result": False,
            "error_type": type(exc).__name__,
            "error_message": exc.detail,
        },
    )


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

fastapi.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

fastapi.include_router(tweets.router, prefix="/api", tags=["api"])
fastapi.include_router(medias.router, prefix="/api", tags=["api"])
fastapi.include_router(users.router, prefix="/api", tags=["api"])
