"""
Owner: Ishaan
ChatService orchestrates: load report context → load history → call LLM → persist.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from openai import OpenAI

from app.core.config import settings
from app.models.chat import ChatSession, ChatMessage
from app.models.report import CreditReport
from app.services.prompts import build_system_prompt, pick_quick_actions

HISTORY_LIMIT = 10            # last N messages (user+assistant)
MAX_INPUT_CHARS = 2000        # guard against giant user msgs

_client: Optional[OpenAI] = None


def _client_lazy() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.openai_api_key,
            base_url="https://api.groq.com/openai/v1",   # Groq endpoint
        )
    return _client


def _latest_report_for_user(db: Session, user_id: int) -> Optional[CreditReport]:
    return (
        db.query(CreditReport)
        .filter(CreditReport.user_id == user_id)
        .order_by(CreditReport.created_at.desc())
        .first()
    )


def _load_history(db: Session, session_id: int) -> List[Dict[str, str]]:
    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
    return [{"role": m.role, "content": m.content} for m in reversed(msgs)]


def _save(db: Session, session_id: int, role: str, content: str) -> ChatMessage:
    m = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def send_message(db: Session, session: ChatSession, user_text: str) -> Dict[str, Any]:
    user_text = (user_text or "").strip()
    if not user_text:
        raise ValueError("empty message")
    if len(user_text) > MAX_INPUT_CHARS:
        user_text = user_text[:MAX_INPUT_CHARS]

    # 1. persist user message first (so it survives crashes)
    user_msg = _save(db, session.id, "user", user_text)

    # 2. build messages payload
    report = _latest_report_for_user(db, session.user_id)
    report_json = report.parsed_json if report else None
    # inject risk_level if available
    if report and isinstance(report_json, dict):
        report_json = {**report_json, "risk_level": report.risk_level}

    system_prompt = build_system_prompt(report_json)
    history = _load_history(db, session.id)  # includes the just-saved user msg

    messages = [{"role": "system", "content": system_prompt}] + history

    # 3. call LLM
    try:
        resp = _client_lazy().chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            max_tokens=settings.openai_max_tokens,
            temperature=0.4,
        )
        reply_text = resp.choices[0].message.content.strip()
    except Exception as e:
        reply_text = ("Sorry, I could not reach the AI service right now. "
                      "Please try again in a moment.")
        # log e in real code
        print("LLM error:", e)

    # 4. persist assistant message
    asst_msg = _save(db, session.id, "assistant", reply_text)

    # 5. quick actions for UI chips
    actions = pick_quick_actions(report_json)

    return {
        "user_message": user_msg,
        "assistant_message": asst_msg,
        "suggested_actions": actions,
    }
