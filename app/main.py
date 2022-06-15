import os

import sqlalchemy
from fastapi import FastAPI, Depends
from fastapi_sqlalchemy import DBSessionMiddleware

from app.authenticate import oauth2_scheme, router as auth_router
from app.create_initial_test_db import engine, create_tables
from app.routers import users, todos

if not sqlalchemy.inspect(engine).has_table('user'):
    create_tables()

app = FastAPI()
app.include_router(users.router)
app.include_router(todos.router)
app.include_router(auth_router)

# env: TEST_DB=sqlite:///app/database.db
# app.add_middleware(DBSessionMiddleware, db_url=os.getenv("TEST_DB"))

sql_url = os.getenv("DB_URL")
app.add_middleware(DBSessionMiddleware, db_url=sql_url)


@app.get("/")
async def home():
    return {"message": "Welcome To Thundervarg!"}


@app.get("/private/")
async def read_private(token: str = Depends(oauth2_scheme)):
    return {"token": token}
