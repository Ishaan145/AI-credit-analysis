"""
Anshul part
OCR raw text → structured JSON (matches schemas.report.ParsedReport)
Approach: regex first-pass + spaCy NER + LLM fallback for messy fields.
"""
import re
from typing import Dict, Any


def parse_ocr_text(raw: str) -> Dict[str, Any]:
    """Minimal regex baseline. Anshul: expand to full ParsedReport shape."""
    score_m = re.search(r"(?:credit\s*score|score)\s*[:\-]?\s*(\d{3})", raw, re.I)
    util_m = re.search(r"utili[sz]ation\s*[:\-]?\s*(\d{1,3})\s*%", raw, re.I)
    return {
        "score": int(score_m.group(1)) if score_m else 0,
        "utilization": float(util_m.group(1)) if util_m else 0.0,
        "payment_history": [],
        "inquiries": [],
        "accounts": [],
        "age_months": 0,
    }
