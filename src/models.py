from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()

followers_association = Table(
    "followers",
    db.metadata,
    Column("follower_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("followed_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
)

class User(db.Model):
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String(40), nullable=False)
    lastname: Mapped[str] = mapped_column(String(40), nullable=False)
    username: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    # Relación Uno a Muchos
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="user")
    
    # Relación Muchos a Muchos Autorreferencial
    followers: Mapped[List["User"]] = relationship(
        "User",
        secondary=followers_association,
        primaryjoin=(id == followers_association.c.followed_id),
        secondaryjoin=(id == followers_association.c.follower_id),
        back_populates="following"
    )
    
    following: Mapped[List["User"]] = relationship(
        "User",
        secondary=followers_association,
        primaryjoin=(id == followers_association.c.follower_id),
        secondaryjoin=(id == followers_association.c.followed_id),
        back_populates="followers"
    )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "username": self.username,
            "is_active": self.is_active
        }

class Post(db.Model):
    __tablename__ = "post"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Relación inversa con User
    user: Mapped["User"] = relationship(back_populates="posts")
    
    # Relación Uno a Muchos con Media
    media: Mapped[List["Media"]] = relationship(back_populates="post")

    def serialize(self):
        return {
            "id": self.id, 
            "user_id": self.user_id,
            "media": [m.serialize() for m in self.media]
        }

class Media(db.Model):
    __tablename__ = "media"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)

    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)
    
    # Relación inversa con Post
    post: Mapped["Post"] = relationship(back_populates="media")
    
    def serialize(self):
        return {
            "id": self.id,
            "url": self.url,
            "type": self.type,
        }