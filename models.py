from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database import Base


class Post(Base):
  __tablename__ = 'posts'

  id: Mapped[int] = mapped_column(primary_key=True)
  content: Mapped[str]
  created_at: Mapped[datetime] = mapped_column(server_default=func.now())
  # created_at: Mapped[datetime]
  comments: Mapped[list['Comment']] = relationship(
    back_populates='post',
    cascade='all, delete-orphan'
  )
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  user: Mapped['User'] = relationship(back_populates='posts')

  likes: Mapped[list['Like']] = relationship(cascade='all, delete-orphan')

class Comment(Base):
  __tablename__ = 'comments'

  id: Mapped[int] = mapped_column(primary_key=True)
  content: Mapped[str]
  created_at: Mapped[datetime] = mapped_column(server_default=func.now())

  #Post(1) : Comment(N)
  post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))
  post: Mapped['Post'] = relationship(back_populates='comments')

  # User(1) : Comment(N)
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  user: Mapped['User'] = relationship()

class User(Base):
  __tablename__ = 'users'

  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(unique=True)
  password_hash: Mapped[str]
  posts: Mapped[list['Post']] = relationship(back_populates='user')
  # comments: Mapped[list['Comment']] = relationship(back_populates='user')

class UserSession(Base):
  __tablename__ = 'sessions'

  # 신분증
  id: Mapped[str] = mapped_column(primary_key=True)
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  created_at: Mapped[datetime] = mapped_column(server_default=func.now())
  user: Mapped['User'] = relationship()

class Like(Base):
  __tablename__ = 'likes'

  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
  post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'), primary_key=True)

