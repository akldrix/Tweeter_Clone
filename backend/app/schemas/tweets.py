from pydantic import BaseModel, Field, model_validator

from app.schemas.users import BaseUser


class TweetCreation(BaseModel):
    tweet_data: str
    tweet_media_ids: list[int] | None = None


class LikeResponse(BaseModel):
    id: int
    user: BaseUser

    model_config = {"from_attributes": True}


class MediaResponse(BaseModel):
    result: bool = True
    media_id: int


class TweetResponse(BaseModel):
    id: int
    content: str = Field(validation_alias="tweet_data")
    attachments: list[str] | None = []
    author: BaseUser
    likes: list[LikeResponse]

    model_config = {"from_attributes": True}


class TweetGetResponse(BaseModel):
    result: bool = True
    tweets: list[TweetResponse]


class TweetCreateResponse(BaseModel):
    result: bool = True
    tweet_id: int

    @model_validator(mode="before")
    @classmethod
    def validate(cls, data: any) -> any:
        if hasattr(data, "media"):
            data.attachments = [m.file_path for m in getattr(data, "media", [])]
        if hasattr(data, "likes"):
            data.likes = [
                {"user_id": like.user_id, "name": like.user.name}
                for like in getattr(data, "likes", [])
            ]

        return data


class TweetDeleteResponse(BaseModel):
    result: bool = True


class TweetLikeResponse(BaseModel):
    result: bool = True
