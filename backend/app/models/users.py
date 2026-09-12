from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.tweets import Tweet

user_following = Table(
    "user_following",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("following_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    passkey: Mapped[str] = mapped_column(String, nullable=False)
    following: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_following,
        primaryjoin=id == user_following.c.user_id,
        secondaryjoin=id == user_following.c.following_id,
        back_populates="followers",
        lazy="selectin",
    )
    followers: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_following,
        primaryjoin=id == user_following.c.following_id,
        secondaryjoin=id == user_following.c.user_id,
        back_populates="following",
        lazy="selectin",
    )
    tweets: Mapped[list["Tweet"]] = relationship(
        "Tweet", back_populates="author", cascade="all, delete-orphan"
    )
