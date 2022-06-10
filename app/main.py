import os

from fastapi import FastAPI, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware, db

from model import Todo, User
from schema import SchemaUser, SchemaTodo, SchemaTodoUpdate

app = FastAPI()
sql_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"

# app.add_middleware(DBSessionMiddleware, db_url="sqlite:///database.db")
app.add_middleware(DBSessionMiddleware, db_url=sql_url)


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


@app.post("/users/", response_model=SchemaUser)
def add_user(user: SchemaUser):
    with db.session as sess:
        sess.expire_on_commit = False
        new_user = User(name=user.name)
        sess.add(new_user)
        sess.commit()
        return new_user


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
