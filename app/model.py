from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    todos: List["Todo"] = Relationship(back_populates="user")


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    due_date: datetime = Field(default_factory=None, nullable=True)

    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="todos")
