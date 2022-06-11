from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db

from app.authenticate import get_password_hash, get_current_active_user
from app.model import User
from app.schema import SchemaUser

router = APIRouter(
    prefix="/users"
)


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/")
def read_users():
    with db.session as sess:
        result = sess.query(User).all()
    return result


@router.get("/{uid}")
def read_user(uid: int):
    with db.session as sess:
        result = sess.query(User).filter(User.id == uid).first()
    return result


@router.post("/", response_model=SchemaUser)
def add_user(user: SchemaUser):
    with db.session as sess:
        sess.expire_on_commit = False
        new_user = User(
            name=user.name,
            password=get_password_hash(user.password),
            disabled=user.disabled,
        )
        sess.add(new_user)
        sess.commit()
    return new_user


@router.delete("/{user_id}")
def delete_user(user_id: int):
    with db.session as sess:
        user = sess.get(User, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found!")

        sess.delete(user)
        sess.commit()

    return {"User deleted": user}

