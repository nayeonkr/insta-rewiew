# insta PJT

- 프로젝트 세팅
```
uv init insta --bare --python 3.14
```

- 필요한 라이브러리 설치
```
uv add "fastapi[standard]" sqlalchemy "psycopg[binary]" alembic
```