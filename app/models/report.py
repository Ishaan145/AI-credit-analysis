from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.core.db import Base


class CreditReport(Base):
    __tablename__ = "credit_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    raw_text = Column(String, nullable=True)              # OCR raw
    parsed_json = Column(JSON, nullable=False)            # structured
    score = Column(Integer, nullable=True)
    utilization = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)            # low/medium/high
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reports")
    factors = relationship("ScoreFactor", back_populates="report", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="report", cascade="all, delete-orphan")


class ScoreFactor(Base):
    __tablename__ = "score_factors"

    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("credit_reports.id", ondelete="CASCADE"), index=True)
    name = Column(String, nullable=False)          # "Payment History"
    value = Column(String, nullable=True)          # "100%" / "4.2 yrs"
    weight = Column(Float, nullable=False)         # 0.35
    impact = Column(String, nullable=True)         # "Excellent"/"Low Impact"

    report = relationship("CreditReport", back_populates="factors")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("credit_reports.id", ondelete="CASCADE"), index=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    priority = Column(Integer, default=1)          # 1 = highest
    rule_key = Column(String, nullable=True)       # which rule fired
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    report = relationship("CreditReport", back_populates="recommendations")
