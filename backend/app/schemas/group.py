from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class GroupOut(BaseModel):
    id: int
    name: str
    description: str
    topics: List[str] = []
    member_count: int = 0
    created_at: datetime
    is_favorite: bool = False
    is_member: bool = False

    class Config:
        from_attributes = True


class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    topics: Optional[List[str]] = []
