from pydantic import BaseModel
from typing import List
from datetime import datetime
from uuid import UUID

class MessageCreate(BaseModel):
    content: str

class MessageOut(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

class MessageList(BaseModel):
    messages: List[MessageOut]