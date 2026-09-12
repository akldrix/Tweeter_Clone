from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_async_session
from app.models.users import User
from app.schemas.users import FollowResponse, ProfileResponse

api_key_header = APIKeyHeader(name="api-key", auto_error=False)


async def get_current_user(
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No api key header provided",
        )
    try:
        query = (
            select(User)
            .where(User.passkey == api_key)
            .options(
                selectinload(User.followers),
                selectinload(User.following),
            )
        )
        result = await session.execute(query)
        user = result.scalar_one()
        return user
    except NoResultFound as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No users with this api key found",
        ) from err


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=ProfileResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return {"result": True, "user": current_user}


@router.get("/{id}", response_model=ProfileResponse)
async def get_profile(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = (
        select(User)
        .where(User.id == id)
        .options(selectinload(User.following), selectinload(User.followers))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"result": True, "user": user}


@router.post("/{id}/follow", response_model=FollowResponse)
async def follow_user(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    user_to_be_followed = await session.scalar(select(User).where(User.id == id))

    follower = await session.scalar(
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.following))
    )

    if not user_to_be_followed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not follower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    follower.following.append(user_to_be_followed)

    await session.commit()

    return {"result": True}


@router.delete("/{id}/follow", response_model=FollowResponse)
async def unfollow_user(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    user_to_be_unfollow = await session.scalar(select(User).where(User.id == id))
    follower = await session.scalar(select(User).where(User.id == current_user.id))

    if not user_to_be_unfollow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not follower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    follower.following.remove(user_to_be_unfollow)

    await session.commit()

    return {"result": True}
