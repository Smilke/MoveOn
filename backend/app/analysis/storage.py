"""Simple storage helper to persist analysis feedback locally.

This writes JSON lines into uploads/analysis_logs.jsonl for easy inspection.
"""
from pathlib import Path
import json
from typing import Dict, Any


def save_feedback(feedback: Dict[str, Any]):
    base_dir = Path(__file__).resolve().parents[1]
    upload_dir = base_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    out_file = upload_dir / "analysis_logs.jsonl"
    with out_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(feedback, ensure_ascii=False) + "\n")
