from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from .database import Base


class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="cascade"), nullable=False
    )
    user = relationship("User")


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Vote(Base):
    __tablename__ = "votes"
    post_id = Column(
        Integer, ForeignKey("posts.post_id", ondelete="cascade"), primary_key=True
    )
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="cascade"), primary_key=True
    )
