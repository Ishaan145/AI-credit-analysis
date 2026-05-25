"""
Owner: Ishaan
GET  /recommendations/{report_id}     list rule-fired recos (persist if not yet)
POST /plan/generate                   action plan (recos + score forecast)
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.report import CreditReport, Recommendation
from app.schemas.report import RecommendationOut
from app.services.reco_engine import generate_recommendations, build_action_plan

router = APIRouter(tags=["coach"])


@router.get("/recommendations/{report_id}", response_model=List[RecommendationOut])
def list_recos(report_id: int, db: Session = Depends(get_db),
               current: User = Depends(get_current_user)):
    r = db.query(CreditReport).filter(
        CreditReport.id == report_id, CreditReport.user_id == current.id
    ).first()
    if not r:
        raise HTTPException(404, "report not found")

    # generate on the fly, cache in DB if empty
    if not r.recommendations:
        for fired in generate_recommendations(r.parsed_json or {}):
            db.add(Recommendation(
                report_id=r.id,
                title=fired["title"],
                body=fired["body"],
                priority=fired["priority"],
                rule_key=fired["rule_key"],
            ))
        db.commit()
        db.refresh(r)
    return r.recommendations


class PlanRequest(BaseModel):
    report_id: int


@router.post("/plan/generate")
def generate_plan(req: PlanRequest, db: Session = Depends(get_db),
                  current: User = Depends(get_current_user)):
    r = db.query(CreditReport).filter(
        CreditReport.id == req.report_id, CreditReport.user_id == current.id
    ).first()
    if not r:
        raise HTTPException(404, "report not found")
    plan = build_action_plan(r.parsed_json or {})
    return {"report_id": r.id, **plan}
