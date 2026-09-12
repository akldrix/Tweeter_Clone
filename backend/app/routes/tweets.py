from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_async_session
from app.models import Like
from app.models.tweets import Media, Tweet
from app.models.users import User
from app.routes.users import get_current_user
from app.schemas.tweets import (
    TweetCreateResponse,
    TweetCreation,
    TweetDeleteResponse,
    TweetGetResponse,
    TweetLikeResponse,
)

router = APIRouter(prefix="/tweets", tags=["tweets"])


@router.post(
    "", response_model=TweetCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_tweet(
    tweet: TweetCreation,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    new_tweet = Tweet(tweet_data=tweet.tweet_data, user_id=current_user.id)
    session.add(new_tweet)
    await session.flush()

    if tweet.tweet_media_ids:
        smth = (
            update(Media)
            .where(Media.id.in_(tweet.tweet_media_ids))
            .values(tweet_id=new_tweet.id)
        )
        await session.execute(smth)

    await session.commit()

    return {"result": True, "tweet_id": new_tweet.id}


@router.get("", response_model=TweetGetResponse)
async def get_tweets(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = (
        select(Tweet)
        .options(
            selectinload(Tweet.author),
            selectinload(Tweet.likes).selectinload(Like.user),
            selectinload(Tweet.media),
        )
        .order_by(Tweet.id.desc())
    )
    result = await session.execute(query)
    tweets = result.scalars().all()

    if not tweets:
        return {"result": True, "tweets": []}

    return {"result": True, "tweets": tweets}


@router.delete("/{id}", response_model=TweetDeleteResponse)
async def delete_tweet(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    tweet_to_delete = await session.scalar(select(Tweet).where(Tweet.id == id))

    if not tweet_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found"
        )

    if tweet_to_delete.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )

    await session.delete(tweet_to_delete)

    await session.commit()

    return {"result": True}


@router.post(
    "/{id}/likes", response_model=TweetLikeResponse, status_code=status.HTTP_201_CREATED
)
async def like_tweet(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    tweet_to_like = await session.scalar(select(Tweet).where(Tweet.id == id))
    if not tweet_to_like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found"
        )

    existing_like = await session.scalar(
        select(Like).where(
            Like.tweet_id == tweet_to_like.id, Like.user_id == current_user.id
        )
    )

    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already liked this tweet"
        )

    like = Like(tweet_id=tweet_to_like.id, user_id=current_user.id)
    session.add(like)

    await session.commit()

    return {"result": True}


@router.delete("/{id}/likes", response_model=TweetLikeResponse)
async def unlike_tweet(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    tweet_to_unlike = await session.scalar(select(Tweet).where(Tweet.id == id))
    if not tweet_to_unlike:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found"
        )

    unlike = await session.scalar(
        select(Like).where(
            Like.tweet_id == tweet_to_unlike.id, Like.user_id == current_user.id
        )
    )

    if not unlike:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You haven't liked this tweet",
        )

    await session.delete(unlike)

    await session.commit()

    return {"result": True}
