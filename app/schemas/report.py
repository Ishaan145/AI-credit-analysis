from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


# --- structured credit report (output of OCR + parser) ---

class PaymentEntry(BaseModel):
    month: str                    # "2024-03"
    status: Literal["on_time", "late_30", "late_60", "late_90+"]


class InquiryEntry(BaseModel):
    date: str
    lender: Optional[str] = None
    type: Literal["hard", "soft"] = "hard"


class AccountEntry(BaseModel):
    type: str                     # "credit_card" | "loan" | "mortgage" ...
    opened: Optional[str] = None
    balance: Optional[float] = None
    limit: Optional[float] = None


class ParsedReport(BaseModel):
    score: int = Field(ge=300, le=900)
    utilization: float = Field(ge=0, le=100)
    payment_history: List[PaymentEntry] = []
    inquiries: List[InquiryEntry] = []
    accounts: List[AccountEntry] = []
    age_months: int = 0


class ReportOut(BaseModel):
    id: int
    score: Optional[int]
    utilization: Optional[float]
    risk_level: Optional[str]
    parsed_json: dict
    created_at: datetime

    class Config:
        from_attributes = True


class FactorOut(BaseModel):
    name: str
    value: Optional[str]
    weight: float
    impact: Optional[str]

    class Config:
        from_attributes = True


class RecommendationOut(BaseModel):
    id: int
    title: str
    body: str
    priority: int
    rule_key: Optional[str]

    class Config:
        from_attributes = True
