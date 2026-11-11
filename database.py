# DB접근에 관련된 코드들
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

DB_URL = 'postgresql+psycopg://sd4:sd4@localhost:5432/insta'
engine = create_engine(DB_URL, echo=True)

class Base(DeclarativeBase):
  pass