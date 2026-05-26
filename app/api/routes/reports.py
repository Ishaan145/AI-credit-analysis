"""
Anshul part
TODO: upload PDF/image → OCR → parser → save CreditReport row.
For now returns 501 so chat side can still mock-test.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.report import CreditReport
from app.schemas.report import ReportOut, FactorOut

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/upload", response_model=ReportOut, status_code=201)
def upload_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    raise HTTPException(501, "implement OCR + parser pipeline")


@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db),
               current: User = Depends(get_current_user)):
    r = db.query(CreditReport).filter(
        CreditReport.id == report_id, CreditReport.user_id == current.id
    ).first()
    if not r:
        raise HTTPException(404, "report not found")
    return r


@router.get("/{report_id}/factors", response_model=list[FactorOut])
def factors(report_id: int, db: Session = Depends(get_db),
            current: User = Depends(get_current_user)):
    r = db.query(CreditReport).filter(
        CreditReport.id == report_id, CreditReport.user_id == current.id
    ).first()
    if not r:
        raise HTTPException(404, "report not found")
    return r.factors


@router.get("/{report_id}/risk")
def risk(report_id: int, db: Session = Depends(get_db),
         current: User = Depends(get_current_user)):
    r = db.query(CreditReport).filter(
        CreditReport.id == report_id, CreditReport.user_id == current.id
    ).first()
    if not r:
        raise HTTPException(404, "report not found")
    return {"risk_level": r.risk_level, "score": r.score, "utilization": r.utilization}
