import os
from datetime import datetime, timedelta

import sqlalchemy
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_sqlalchemy import DBSessionMiddleware, db
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel

from app.create_initial_test_db import engine, create_tables
from app.model import Todo, User
from app.schema import SchemaUser, SchemaTodo, SchemaTodoUpdate

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()

# env: TEST_DB=sqlite:///app/database.db
# app.add_middleware(DBSessionMiddleware, db_url=os.getenv("TEST_DB"))

sql_url = os.getenv("DB_URL")
app.add_middleware(DBSessionMiddleware, db_url=sql_url)

if not sqlalchemy.inspect(engine).has_table('user'):
    create_tables()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str) -> User:
    with db.session as sess:
        user = sess.query(User).filter(User.name == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
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


@app.post("/users/", response_model=SchemaUser)
def add_user(user: SchemaUser):
    with db.session as sess:
        sess.expire_on_commit = False
        new_user = User(name=user.name,  password=get_password_hash(user.password), disabled=user.disabled)
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
