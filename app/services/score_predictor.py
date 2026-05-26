"""
Anshul part
v1 weighted delta formula. v2 train RandomForest on synthetic dataset.
"""
from typing import Dict, Any

# FICO weights
W_PAY = 0.35
W_UTIL = 0.30
W_AGE = 0.15
W_MIX = 0.10
W_INQ = 0.10

SCALE = 200   # rough mapping of normalized delta → score points (tune empirically)


def predict_delta(current: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
    """
    current: parsed report.
    action: {target_utilization, on_time_rate_delta, inquiry_reduction, months_horizon}
    Returns: {delta, projected_score, months}
    """
    util_now = current.get("utilization", 50)
    util_target = action.get("target_utilization", util_now)
    util_delta_norm = max(0.0, (util_now - util_target)) / 100.0

    pay_delta = action.get("on_time_rate_delta", 0.0)  # 0..1
    inq_red = action.get("inquiry_reduction", 0)       # count
    inq_delta_norm = min(1.0, inq_red / 5.0)

    months = action.get("months_horizon", 6)
    age_delta_norm = min(1.0, months / 24.0)

    delta = (
        util_delta_norm * W_UTIL
        + pay_delta * W_PAY
        + inq_delta_norm * W_INQ
        + age_delta_norm * W_AGE
    ) * SCALE

    projected = min(900, int(current.get("score", 0) + delta))
    return {"delta": round(delta, 1), "projected_score": projected, "months": months}
