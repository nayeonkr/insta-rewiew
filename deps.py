from fastapi import Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from typing import Annotated
from database import engine
from models import User, Post, UserSession


templates = Jinja2Templates(directory='templates')
password_hash = PasswordHash.recommended()

def get_db():
  with Session(engine) as db:
    yield db

SessionDep = Annotated[Session, Depends(get_db)]

def get_post_or_404(post_id: int, db: SessionDep):
  # SELECT * FROM posts WHERE post_id = 10;
  post = db.get(Post, post_id)

  if post is None:
    # from fastapi import HTTPException
    raise HTTPException(status_code=404, detail='해당 게시물이 없습니다.')
  
  return post

PostDep = Annotated[Post, Depends(get_post_or_404)]


def get_current_user(request: Request, db: SessionDep):
  session_id = request.cookies.get('session_id')

  # 신분증 유무 판단
  if session_id is None:
    return None

  user_session = db.get(UserSession, session_id)

  # 신분증 유효한지 검사
  if user_session is None:
    return None

  return user_session.user

CurrentUserDep = Annotated[User | None, Depends(get_current_user)]

  
