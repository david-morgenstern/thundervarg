from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SchemaUser(BaseModel):
    name: str
    password: str
    disabled: bool = False

    class Config:
        orm_mode = True


class SchemaTodo(BaseModel):
    name: str
    description: str
    due_date: datetime

    owner_id: int

    class Config:
        orm_mode = True


class SchemaTodoUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    due_date: Optional[datetime] = None

    owner_id: Optional[int] = None

    class Config:
        orm_mode = True
