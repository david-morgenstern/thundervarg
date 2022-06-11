from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db

from app.model import Todo
from app.schema import SchemaTodoUpdate, SchemaTodo

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not Found!"}}
)


@router.get("/")
def get_todos():
    with db.session as sess:
        todos = sess.query(Todo).all()

    return todos


@router.get("/{todo_id}")
def get_todo(todo_id: int):
    with db.session as sess:
        todo = sess.query(Todo).filter(Todo.id == todo_id).first()

    return todo


@router.get("/user/{user_id}")
def get_todos_by_user(user_id: int):
    with db.session as sess:
        todos = sess.query(Todo).filter(Todo.owner_id == user_id).all()

    return todos


@router.post("/", response_model=SchemaTodo)
def add_todo(todo: SchemaTodo):
    with db.session as sess:
        sess.expire_on_commit = False
        new_todo = Todo(**todo.dict())
        sess.add(new_todo)
        sess.commit()

    return new_todo


@router.patch("/{todo_id}", response_model=SchemaTodoUpdate)
async def update_todo(todo_id: int, todo: SchemaTodoUpdate):
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


@router.delete("/{todo_id}")
def delete_todo(todo_id: int):
    with db.session as sess:
        todo = sess.get(Todo, todo_id)

        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found!")

        sess.delete(todo)
        sess.commit()

    return {"Todo deleted": todo}
