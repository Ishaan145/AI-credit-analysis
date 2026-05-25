"""
Owner: Ishaan
Rule-driven recommendation engine. LLM polish optional (toggle).
Input: parsed report dict (see schemas.report.ParsedReport)
Output: list[dict] of {title, body, priority, rule_key}
"""
from typing import Dict, Any, List

# --- Static rules, ordered by FICO factor weight (highest impact first) ---
# Each rule: condition(report) -> dict | None
# priority 1 = highest

def _rule_payment_history(r: Dict[str, Any]):
    late = [p for p in r.get("payment_history", []) if p.get("status", "").startswith("late")]
    if late:
        return {
            "rule_key": "late_payments",
            "priority": 1,
            "title": "Set up autopay",
            "body": f"You have {len(late)} late payment(s). Payment history is 35% of your score — "
                    f"the biggest single factor. Enable autopay for at least the minimum due on "
                    f"every account to stop new late marks.",
        }
    return None


def _rule_utilization(r: Dict[str, Any]):
    util = r.get("utilization", 0)
    if util > 30:
        return {
            "rule_key": "high_utilization",
            "priority": 2,
            "title": "Reduce utilization below 30%",
            "body": f"Your credit utilization is {util:.0f}%. Lenders prefer <30%, ideally <10%. "
                    f"Pay down balances or request a credit-limit increase to lower the ratio.",
        }
    return None


def _rule_inquiries(r: Dict[str, Any]):
    hard = [i for i in r.get("inquiries", []) if i.get("type") == "hard"]
    if len(hard) > 4:
        return {
            "rule_key": "too_many_inquiries",
            "priority": 3,
            "title": "Pause new credit applications",
            "body": f"You have {len(hard)} hard inquiries. Each can drop your score 5–10 points. "
                    f"Avoid new credit applications for the next 6 months.",
        }
    return None


def _rule_credit_age(r: Dict[str, Any]):
    age = r.get("age_months", 0)
    if age < 24:
        return {
            "rule_key": "young_credit_age",
            "priority": 4,
            "title": "Keep your oldest account open",
            "body": f"Your average credit age is {age} months. Length of history is 15% of your "
                    f"score. Do not close old cards — let them age.",
        }
    return None


def _rule_credit_mix(r: Dict[str, Any]):
    types = {a.get("type") for a in r.get("accounts", [])}
    if len(types) < 2:
        return {
            "rule_key": "thin_credit_mix",
            "priority": 5,
            "title": "Diversify your credit mix",
            "body": "Credit mix is 10% of your score. A small secured loan or another card type "
                    "(installment vs revolving) can help once your utilization is under control.",
        }
    return None


RULES = [
    _rule_payment_history,
    _rule_utilization,
    _rule_inquiries,
    _rule_credit_age,
    _rule_credit_mix,
]


def generate_recommendations(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for rule in RULES:
        fired = rule(report)
        if fired:
            out.append(fired)
    out.sort(key=lambda x: x["priority"])
    return out


def build_action_plan(report: Dict[str, Any], max_steps: int = 5) -> Dict[str, Any]:
    """Combines top N recos + estimated impact (calls score_predictor)."""
    from app.services.score_predictor import predict_delta

    recos = generate_recommendations(report)[:max_steps]

    # heuristic action vector based on which rules fired
    rule_keys = {r["rule_key"] for r in recos}
    action = {
        "target_utilization": 25 if "high_utilization" in rule_keys else report.get("utilization", 30),
        "on_time_rate_delta": 0.10 if "late_payments" in rule_keys else 0.0,
        "inquiry_reduction": 3 if "too_many_inquiries" in rule_keys else 0,
        "months_horizon": 6,
    }
    forecast = predict_delta(report, action)

    return {
        "steps": recos,
        "forecast": forecast,
    }
