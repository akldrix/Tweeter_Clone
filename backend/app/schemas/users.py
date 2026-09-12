from pydantic import BaseModel


class BaseUser(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class UserResponse(BaseUser):
    following: list["BaseUser"]
    followers: list["BaseUser"]


class ProfileResponse(BaseModel):
    result: bool = True
    user: UserResponse


class FollowResponse(BaseModel):
    result: bool = True
