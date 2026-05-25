from app.services.reco_engine import generate_recommendations, build_action_plan
from app.services.prompts import build_system_prompt, pick_quick_actions


def _sample_bad_report():
    return {
        "score": 645,
        "utilization": 78,
        "payment_history": [
            {"month": "2024-01", "status": "on_time"},
            {"month": "2024-02", "status": "late_30"},
        ],
        "inquiries": [{"type": "hard"} for _ in range(6)],
        "accounts": [{"type": "credit_card"}],
        "age_months": 14,
    }


def test_rules_fire_for_bad_report():
    recos = generate_recommendations(_sample_bad_report())
    keys = {r["rule_key"] for r in recos}
    assert "late_payments" in keys
    assert "high_utilization" in keys
    assert "too_many_inquiries" in keys
    assert "young_credit_age" in keys
    assert "thin_credit_mix" in keys
    # priority ordering
    assert recos[0]["priority"] <= recos[-1]["priority"]


def test_action_plan_forecast_positive_delta():
    plan = build_action_plan(_sample_bad_report())
    assert plan["forecast"]["delta"] > 0
    assert plan["forecast"]["projected_score"] >= 645


def test_prompt_includes_real_numbers():
    p = build_system_prompt(_sample_bad_report())
    assert "645" in p
    assert "78" in p


def test_quick_actions_match_problems():
    qa = pick_quick_actions(_sample_bad_report())
    assert "Improve Utilization" in qa
    assert "Remove Late Payments" in qa
