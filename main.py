from fastapi import FastAPI, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

DB_URL = 'postgresql+psycopg://sd4:sd4@localhost:5432/insta'
engine = create_engine(DB_URL, echo=True)

# 모델 정의
class Base(DeclarativeBase):
  pass

class Post(Base):
  __tablename__ = 'posts'

  id: Mapped[int] = mapped_column(primary_key=True)
  content: Mapped[str]

app = FastAPI()
templates = Jinja2Templates(directory='templates')

def get_db():
  with Session(engine) as db:
    yield db

@app.get('/')
def home():
  return {'hi': 'hello'}


@app.get('/posts')
def post_list(request: Request, db: Session = Depends(get_db)):
  # with Session(engine) as db:
  
  posts = db.scalars(select(Post)).all()
  return templates.TemplateResponse(
    request=request,
    name='list.html',
    context={'posts': posts}
  )


@app.get('/posts/new')
def post_new(request: Request):
  return templates.TemplateResponse(
    request=request,
    name='new.html'
  )


@app.post('/posts/create')
def post_create(content: str = Form(), db: Session = Depends(get_db)):
  # db = Session(engine)
  post = Post(content=content)
  db.add(post)
  db.commit()

  # from fastapi.responses import RedirectResponse
  return RedirectResponse('/posts', status_code=303)