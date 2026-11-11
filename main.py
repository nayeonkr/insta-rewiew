from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, select, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from datetime import datetime
from pwdlib import PasswordHash
import secrets
from typing import Annotated
from routers import posts, auth

app = FastAPI()

app.include_router(posts.router)
app.include_router(auth.router)


@app.get('/')
def home():
  return {'hi': 'hello'}


