from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class SessionCreate(BaseModel):
    title: Optional[str] = "New chat"


class SessionOut(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageIn(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatReply(BaseModel):
    user_message: MessageOut
    assistant_message: MessageOut
    suggested_actions: List[str] = []      # quick-action chips on screen 3
