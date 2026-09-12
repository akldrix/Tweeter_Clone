from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.users import User


class Tweet(Base):
    __tablename__ = "tweets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    author: Mapped["User"] = relationship("User", back_populates="tweets")
    likes: Mapped[list["Like"]] = relationship(
        "Like", back_populates="tweet", cascade="all, delete-orphan"
    )
    tweet_data: Mapped[str] = mapped_column(String, nullable=False)
    media: Mapped[list["Media"]] = relationship(
        "Media", back_populates="tweet", cascade="all, delete-orphan", lazy="selectin"
    )

    @property
    def attachments(self) -> list[str]:
        return [m.file_path for m in self.media]


class Media(Base):
    __tablename__ = "medias"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    tweet_id: Mapped[int | None] = mapped_column(
        ForeignKey("tweets.id", ondelete="SET NULL"), nullable=True
    )
    tweet: Mapped[Optional["Tweet"]] = relationship("Tweet", back_populates="media")


class Like(Base):
    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey("tweets.id", ondelete="CASCADE"), nullable=False
    )

    tweet: Mapped["Tweet"] = relationship("Tweet", back_populates="likes")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship("User")
