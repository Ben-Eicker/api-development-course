from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    email: str
    password: str


class UserCreate(UserBase):
    pass


class UserResponse(BaseModel):
    user_id: int
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(UserBase):
    pass


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    post_id: int
    created_at: datetime
    user: UserResponse
    votes: int = 0

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class VoteBase(BaseModel):
    post_id: int
    dir: Literal[0, 1]
