"""
Anshul part
Rule-based risk classifier. Extend with more rules.
"""
from typing import Dict, Any, Literal

Risk = Literal["low", "medium", "high"]


def classify_risk(report: Dict[str, Any]) -> Risk:
    score = report.get("score", 0)
    util = report.get("utilization", 100)
    late = sum(1 for p in report.get("payment_history", []) if p.get("status", "").startswith("late"))
    inquiries = sum(1 for i in report.get("inquiries", []) if i.get("type") == "hard")

    if score >= 750 and util < 30 and late == 0 and inquiries <= 1:
        return "low"
    if score >= 650 and util < 50 and late <= 2 and inquiries <= 4:
        return "medium"
    return "high"
