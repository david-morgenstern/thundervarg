import os
from datetime import timedelta

import sqlalchemy
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_sqlalchemy import DBSessionMiddleware, db

from app.authenticate import Token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, oauth2_scheme, \
    get_password_hash
from app.create_initial_test_db import engine, create_tables
from app.model import Todo, User
from app.schema import SchemaTodoUpdate, SchemaTodo

app = FastAPI()

# env: TEST_DB=sqlite:///app/database.db
# app.add_middleware(DBSessionMiddleware, db_url=os.getenv("TEST_DB"))

sql_url = os.getenv("DB_URL")
app.add_middleware(DBSessionMiddleware, db_url=sql_url)

if not sqlalchemy.inspect(engine).has_table('user'):
    create_tables()


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/private/")
async def read_private(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.get("/users/")
def read_users():
    with db.session as sess:
        result = sess.query(User).all()
    return result


@app.get("/users/{uid}")
def read_user(uid: int):
    with db.session as sess:
        result = sess.query(User).filter(User.id == uid).first()
    return result


@app.post("/users/", response_model=User)
def add_user(user: User):
    with db.session as sess:
        sess.expire_on_commit = False
        new_user = User(name=user.name, password=get_password_hash(user.password), disabled=user.disabled)
        sess.add(new_user)
        sess.commit()
    return new_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    with db.session as sess:
        user = sess.get(User, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="Todo not found!")

        sess.delete(user)
        sess.commit()

    return {"User deleted": user}


@app.get("/todos/")
def get_todos():
    with db.session as sess:
        todos = sess.query(Todo).all()

    return todos


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    with db.session as sess:
        todo = sess.query(Todo).filter(Todo.id == todo_id).first()

    return todo


@app.get("/user-todos/{user_id}")
def get_todos_by_user(user_id: int):
    with db.session as sess:
        todos = sess.query(Todo).filter(Todo.owner_id == user_id).all()

    return todos


@app.post("/todos/", response_model=SchemaTodo)
def add_todo(todo: SchemaTodo):
    with db.session as sess:
        sess.expire_on_commit = False
        new_todo = Todo(**todo.dict())
        sess.add(new_todo)
        sess.commit()

    return new_todo


@app.patch("/todos/{todo_id}", response_model=SchemaTodoUpdate)
def update_todo(todo_id: int, todo: SchemaTodoUpdate):
    with db.session as sess:
        db_todo = sess.get(Todo, todo_id)

        if not db_todo:
            raise HTTPException(status_code=404, detail="Todo not found!")

        for key, value in todo.dict(exclude_unset=True).items():
            setattr(db_todo, key, value)

        sess.add(db_todo)
        sess.commit()
        sess.refresh(db_todo)

    return db_todo


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    with db.session as sess:
        todo = sess.get(Todo, todo_id)

        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found!")

        sess.delete(todo)
        sess.commit()

    return {"Todo deleted": todo}
