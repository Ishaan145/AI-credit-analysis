"""
Owner: Ishaan
Prompt templates for AI Coach. Keep prompts versioned + tested.
"""
import json
from typing import Dict, Any, List

SYSTEM_BASE = """You are "AI Coach" inside a credit-health app. You help the user understand and improve their credit score.

Rules you must follow:
- Be specific, actionable, friendly. Plain English. No jargon dumps.
- Maximum 3 suggestions per reply. Number them.
- Always ground advice in the user's actual report data shown below — refer to their real numbers.
- Never invent numbers. If a field is missing in the report, say so and ask for it.
- Never give legal, tax, or investment advice. Stay on credit-health topics.
- Refuse politely if asked something unrelated to credit, debt, or financial readiness.
- If user is anxious or upset, acknowledge briefly, then move to action.

Output format:
- Short opening sentence (1 line max).
- Numbered list of up to 3 concrete steps.
- Optional closing question to drive the next step.
"""


def build_system_prompt(report_json: Dict[str, Any] | None) -> str:
    if not report_json:
        return SYSTEM_BASE + "\n\n[No credit report uploaded yet. Encourage user to upload one.]"
    compact = {
        "score": report_json.get("score"),
        "utilization_pct": report_json.get("utilization"),
        "age_months": report_json.get("age_months"),
        "late_payments": sum(1 for p in report_json.get("payment_history", [])
                             if p.get("status", "").startswith("late")),
        "hard_inquiries": sum(1 for i in report_json.get("inquiries", [])
                              if i.get("type") == "hard"),
        "account_types": sorted({a.get("type") for a in report_json.get("accounts", []) if a.get("type")}),
        "risk_level": report_json.get("risk_level"),
    }
    return SYSTEM_BASE + "\n\nUser report (compact):\n" + json.dumps(compact, indent=2)


# --- Quick-action chips shown in screen 3 of the demo ---
QUICK_ACTIONS_DEFAULT = [
    "Improve Utilization",
    "Remove Late Payments",
    "Reduce Inquiries",
    "Build Credit Age",
]


def pick_quick_actions(report_json: Dict[str, Any] | None) -> List[str]:
    if not report_json:
        return ["Upload your credit report", "How does FICO work?", "What is a good score?"]
    out = []
    if (report_json.get("utilization") or 0) > 30:
        out.append("Improve Utilization")
    if any(p.get("status", "").startswith("late") for p in report_json.get("payment_history", [])):
        out.append("Remove Late Payments")
    if sum(1 for i in report_json.get("inquiries", []) if i.get("type") == "hard") > 4:
        out.append("Reduce Inquiries")
    if (report_json.get("age_months") or 0) < 24:
        out.append("Build Credit Age")
    return out or QUICK_ACTIONS_DEFAULT[:3]
