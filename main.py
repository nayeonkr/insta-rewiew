from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, select, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from datetime import datetime
from pwdlib import PasswordHash
import secrets

DB_URL = 'postgresql+psycopg://sd4:sd4@localhost:5432/insta'
engine = create_engine(DB_URL, echo=True)

# 모델 정의
class Base(DeclarativeBase):
  pass

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

class Comment(Base):
  __tablename__ = 'comments'

  id: Mapped[int] = mapped_column(primary_key=True)
  content: Mapped[str]
  created_at: Mapped[datetime] = mapped_column(server_default=func.now())
  post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))
  post: Mapped['Post'] = relationship(back_populates='comments')


class User(Base):
  __tablename__ = 'users'

  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(unique=True)
  password_hash: Mapped[str]
  posts: Mapped[list['Post']] = relationship(back_populates='user')


class UserSession(Base):
  __tablename__ = 'sessions'

  # 신분증
  id: Mapped[str] = mapped_column(primary_key=True)
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  created_at: Mapped[datetime] = mapped_column(server_default=func.now())
  user: Mapped['User'] = relationship()



app = FastAPI()
templates = Jinja2Templates(directory='templates')
password_hash = PasswordHash.recommended()

def get_db():
  with Session(engine) as db:
    yield db

def get_post_or_404(post_id: int, db: Session = Depends(get_db)):
  # SELECT * FROM posts WHERE post_id = 10;
  post = db.get(Post, post_id)

  if post is None:
    # from fastapi import HTTPException
    raise HTTPException(status_code=404, detail='해당 게시물이 없습니다.')
  
  return post


def get_current_user(request: Request, db: Session = Depends(get_db)):
  session_id = request.cookies.get('session_id')

  # 신분증 유무 판단
  if session_id is None:
    return None

  user_session = db.get(UserSession, session_id)

  # 신분증 유효한지 검사
  if user_session is None:
    return None

  return user_session.user

  

  



@app.get('/')
def home():
  return {'hi': 'hello'}


@app.get('/posts')
def post_list(
  request: Request, 
  db: Session = Depends(get_db),
  user: User | None = Depends(get_current_user)
):
  # with Session(engine) as db:
  
  # posts = db.scalars(select(Post)).all()
  posts = db.scalars(select(Post).order_by(Post.created_at.desc())).all()
  return templates.TemplateResponse(
    request=request,
    name='list.html',
    context={'posts': posts, 'user': user }
  )


@app.get('/posts/new')
def post_new(
  request: Request,
  user: User | None = Depends(get_current_user)
):
  # 로그인 하지 않은사람이라면
  if user is None:
    return RedirectResponse('/login', status_code=303)
 
  return templates.TemplateResponse(
    request=request,
    name='new.html',
    context={'user': user}
  )


@app.post('/posts/create')
def post_create(
  content: str = Form(), 
  db: Session = Depends(get_db),
  user: User | None = Depends(get_current_user)
):
  if user is None:
    return RedirectResponse('/login', status_code=303)

  # db = Session(engine)
  post = Post(content=content)
  db.add(post)
  db.commit()

  # from fastapi.responses import RedirectResponse
  return RedirectResponse('/posts', status_code=303)


@app.get('/posts/{post_id}')
def post_detail(
  request: Request, 
  post: Post = Depends(get_post_or_404),
  user: User | None = Depends(get_current_user)
):
  # comments = db.scalars(select(Comment).where().order_by(Comment.created_at.desc()))
  return templates.TemplateResponse(
    request=request,
    name='detail.html',
    context={
      'post': post,
      'user': user
    }
  )


@app.get('/posts/{post_id}/edit')
def post_edit(
  request: Request, 
  post: Post = Depends(get_post_or_404),
  user: User | None = Depends(get_current_user)
):
  return templates.TemplateResponse(
    request=request,
    name='edit.html',
    context={
      'post': post,
      'user': user
    }
  )


@app.post('/posts/{post_id}/update')
def post_update(
  content: str = Form(), 
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db)
):
  post.content = content
  db.commit()

  return RedirectResponse('/posts', status_code=303)


@app.post('/posts/{post_id}/delete')
def post_delete(
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db)
):
  db.delete(post)
  db.commit()
  return RedirectResponse('/posts', status_code=303)


@app.post('/posts/{post_id}/comments/create')
def comment_create(
  content: str = Form(),
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db)
):
  comment = Comment(content=content, post=post)
  db.add(comment)
  db.commit()

  return RedirectResponse(f'/posts/{post.id}', status_code=303)


@app.post('/posts/{post_id}/comments/{comment_id}/delete')
def comment_delete(post_id: int, comment_id: int, db: Session = Depends(get_db)):
  comment = db.get(Comment, comment_id)
  db.delete(comment)
  db.commit()

  return RedirectResponse(f'/posts/{post_id}', status_code=303)


# a태그를 통해서 들어오는 signup
@app.get('/signup')
def signup_form(
  request: Request,
  user: User | None = Depends(get_current_user)
):
  return templates.TemplateResponse(
    request=request,
    name='signup.html',
    context={
      'user': user
    }
  )


# form method='post' 방식으로 들어오는 signup
@app.post('/signup')
def signup(
  request: Request,
  username: str = Form(), 
  password: str = Form(),
  db: Session = Depends(get_db)
):
  # 이미 있는 유저인지 검증
  # SELECT * FROM users WHERE username='changhee'
  exists = db.scalar(   select(User).where(User.username == username)  )
  
  # 이미 유저네임을 사용하는 경우 
  if exists:
    return templates.TemplateResponse(
      request=request,
      name='signup.html',
      context={'error': '이미 있는 아이디입니다.'}
    )

  
  # password를 암호화
  # from pwdlib import PasswordHash
  
  hashed_pw = password_hash.hash(password)

  user = User(username=username, password_hash=hashed_pw)
  db.add(user)
  db.commit()

  return RedirectResponse('/login', status_code=303)


@app.get('/login')
def login_form(
  request: Request,
  user: User | None = Depends(get_current_user)
):
  return templates.TemplateResponse(
    request=request,
    name='login.html',
    context={'user': user}
  )


@app.post('/login')
def login(
  request: Request,
  username: str = Form(),
  password: str = Form(),
  db: Session = Depends(get_db)
):
  # 방금 입력한 아이디에 해당하는 유저 찾기
  user = db.scalar(select(User).where(User.username == username))

  # password_hash.verify(password, user.password_hash)
  # 유저가 존재하지 않거나 / 그 유저의 비밀번호와 방금 입력한 비밀번호가 다른경우 => 에러입니다.
  if (user is None) or not (password_hash.verify(password, user.password_hash)):
    return templates.TemplateResponse(
      request=request,
      name='login.html',
      context={'error': '아이디가 존재하지 않거나 비밀번호가 틀렸습니다.'}
    )

  # 비밀번호가 일치하면 => 신분증 발행
  session_id = secrets.token_urlsafe(32)
  # 발행한 신분증을 DB에 저장
  user_session = UserSession(id=session_id, user=user)
  db.add(user_session)
  db.commit()

  # 신분증을 유저한테 전달 (쿠키에 저장시키기)
  response = RedirectResponse('/posts', status_code=303)
  response.set_cookie('session_id', session_id, httponly=True, samesite='lax')
  return response


@app.post('/logout')
def logout(request: Request, db: Session = Depends(get_db)):
  # 신분증 정보 가져오기 
  session_id = request.cookies.get('session_id') 
  user_session = db.get(UserSession, session_id)

  if user_session:
    db.delete(user_session)
    db.commit()

  response = RedirectResponse('/posts', status_code=303)
  response.delete_cookie('session_id')
  return response

