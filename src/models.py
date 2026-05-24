from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Table, Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()

# 1. Tabla de asociación Muchos a Muchos para Seguidores
follower = Table(
    "follower",
    db.metadata,
    Column("user_from_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("user_to_id", Integer, ForeignKey("user.id"), primary_key=True)
)

# 2. Modelo de Usuario


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String(40), nullable=False)
    lastname: Mapped[str] = mapped_column(String(40), nullable=False)
    username: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    # Relación Uno a Muchos con Post
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="user")

    # Relación Uno a Muchos con Comment
    comments: Mapped[List["Comment"]] = relationship(back_populates="author")

    # Relación Muchos a Muchos Autorreferencial (Seguidores)
    followers: Mapped[List["User"]] = relationship(
        "User",
        secondary=follower,
        primaryjoin=(id == follower.c.user_to_id),
        secondaryjoin=(id == follower.c.user_from_id),
        back_populates="following"
    )

    following: Mapped[List["User"]] = relationship(
        "User",
        secondary=follower,
        primaryjoin=(id == follower.c.user_from_id),
        secondaryjoin=(id == follower.c.user_to_id),
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

# 3. Modelo de Publicación


class Post(db.Model):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Relación inversa con User
    user: Mapped["User"] = relationship(back_populates="posts")

    # Relación Uno a Muchos con Media
    media: Mapped[List["Media"]] = relationship(back_populates="post")

    # Relación Uno a Muchos con Comment
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="post_public")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "media": [m.serialize() for m in self.media]
        }

# 4. Modelo de Contenido Multimedia


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

# 5. Modelo de Comentario


class Comment(db.Model):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    comment_text: Mapped[str] = mapped_column(String(255), nullable=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)

    # Relaciones que completan los espejos con User y Post
    author: Mapped["User"] = relationship(back_populates="comments")
    post_public: Mapped["Post"] = relationship(back_populates="comments")
