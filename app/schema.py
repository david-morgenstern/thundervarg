from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class SchemaTodoUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    due_date: Optional[datetime] = None

    owner_id: Optional[int] = None
