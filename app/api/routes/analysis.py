"""
Anshul part
POST /predict  → projected score given an action vector.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.report import CreditReport
from app.services.score_predictor import predict_delta

router = APIRouter(tags=["predict"])


class PredictIn(BaseModel):
    report_id: int
    target_utilization: Optional[float] = None
    on_time_rate_delta: float = 0.0          # 0..1
    inquiry_reduction: int = 0
    months_horizon: int = 6


@router.post("/predict")
def predict(payload: PredictIn, db: Session = Depends(get_db),
            current: User = Depends(get_current_user)):
    r = db.query(CreditReport).filter(
        CreditReport.id == payload.report_id, CreditReport.user_id == current.id
    ).first()
    if not r:
        raise HTTPException(404, "report not found")
    action = payload.model_dump()
    if action["target_utilization"] is None:
        action["target_utilization"] = r.utilization or 30
    return predict_delta(r.parsed_json or {}, action)
