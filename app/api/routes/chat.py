"""
Owner: Ishaan
POST /chat/sessions                       new session
GET  /chat/sessions                       list user's sessions
GET  /chat/sessions/{id}                  history
POST /chat/sessions/{id}/message          send msg, get reply
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    SessionCreate, SessionOut, MessageIn, MessageOut, ChatReply,
)
from app.services.chat_service import send_message

router = APIRouter(prefix="/chat", tags=["chat"])


def _get_session_or_404(db: Session, session_id: int, user_id: int) -> ChatSession:
    s = db.query(ChatSession).filter(
        ChatSession.id == session_id, ChatSession.user_id == user_id
    ).first()
    if not s:
        raise HTTPException(404, "session not found")
    return s


@router.post("/sessions", response_model=SessionOut, status_code=201)
def create_session(payload: SessionCreate, db: Session = Depends(get_db),
                   current: User = Depends(get_current_user)):
    s = ChatSession(user_id=current.id, title=payload.title or "New chat")
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.get("/sessions", response_model=List[SessionOut])
def list_sessions(db: Session = Depends(get_db),
                  current: User = Depends(get_current_user)):
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current.id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


@router.get("/sessions/{session_id}", response_model=List[MessageOut])
def get_history(session_id: int, db: Session = Depends(get_db),
                current: User = Depends(get_current_user)):
    s = _get_session_or_404(db, session_id, current.id)
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == s.id)
        .order_by(ChatMessage.id.asc())
        .all()
    )


@router.post("/sessions/{session_id}/message", response_model=ChatReply)
def post_message(session_id: int, payload: MessageIn,
                 db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    s = _get_session_or_404(db, session_id, current.id)
    try:
        result = send_message(db, s, payload.content)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return result
