import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import User


@pytest.mark.anyio
async def test_get_user_profile(client, test_user_1):
    response = await client.get(f"/api/users/{test_user_1.id}")

    assert response.status_code == 200
    assert response.json() == {
        "result": True,
        "user": {
            "id": test_user_1.id,
            "name": test_user_1.name,
            "following": [],
            "followers": [],
        },
    }


@pytest.mark.anyio
async def test_user_follow(client, db_session, test_user_1, test_user_2):
    user_1_id = test_user_1.id
    user_2_id = test_user_2.id

    response = await client.post(f"/api/users/{test_user_2.id}/follow")

    assert response.status_code == 200

    db_session.expire_all()

    query = (
        select(User).where(User.id == user_1_id).options(selectinload(User.following))
    )

    result = await db_session.execute(query)

    user = result.scalar_one()

    assert user.following[0].id == user_2_id


@pytest.mark.anyio
async def test_user_unfollow(client, db_session, test_user_1, test_user_2):
    user_1_id = test_user_1.id

    follow = await client.post(f"/api/users/{test_user_2.id}/follow")

    assert follow is not None

    response = await client.delete(f"/api/users/{test_user_2.id}/follow")

    assert response.status_code == 200
    assert response.json()["result"] is True

    db_session.expire_all()

    query = (
        select(User).where(User.id == user_1_id).options(selectinload(User.following))
    )

    result = await db_session.execute(query)
    user = result.scalar_one()

    assert len(user.following) == 0


@pytest.mark.anyio
async def test_get_me(client, test_user_1):
    response = await client.get("/api/users/me")

    assert response.status_code == 200

    assert response.json()["result"] is True


@pytest.mark.anyio
async def test_tweets(client, test_user_1):
    tweet_data = {"tweet_data": "Some data"}
    response = await client.post("/api/tweets", json=tweet_data)

    assert response.status_code == 201

    assert response.json()["result"] is True
    assert "tweet_id" in response.json()


@pytest.mark.anyio
async def test_get_tweets(client, test_user_1):
    response = await client.get("/api/tweets")

    assert response.status_code == 200
    assert response.json()["result"] is True


@pytest.mark.anyio
async def test_delete_tweet(client, test_user_1):
    tweet_data = {"tweet_data": "Some data"}
    creation = await client.post("/api/tweets", json=tweet_data)

    tweet_id = creation.json().get("tweet_id")
    assert tweet_id is not None

    response = await client.delete(f"/api/tweets/{tweet_id}")

    assert response.status_code == 200
    assert response.json()["result"] is True


@pytest.mark.anyio
async def test_like(client, test_tweet):
    response = await client.post(f"/api/tweets/{test_tweet.id}/likes")

    assert response.status_code == 201
    assert response.json()["result"] is True


@pytest.mark.anyio
async def test_unlike(client, test_tweet):
    like = await client.post(f"/api/tweets/{test_tweet.id}/likes")
    assert like.status_code == 201

    response = await client.delete(f"/api/tweets/{test_tweet.id}/likes")

    assert response.status_code == 200
    assert response.json()["result"] is True


@pytest.mark.anyio
async def test_media(client, test_media):
    test_file = {
        "file": ("test_image.png", b"test_image_data", "image/png"),
    }
    response = await client.post("/api/medias", files=test_file)

    assert response.status_code == 201
    assert response.json()["result"] is True
