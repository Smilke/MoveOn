"""Runtime helpers for video analysis.

Goals:
- Reuse a single YOLO model instance (avoid re-loading per request)
- Run analysis asynchronously (background thread pool) so uploads return quickly

This is intentionally lightweight (no Redis/Celery) to fit the current project.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, Future
from typing import Any, Dict, Optional
import threading
import os
from datetime import datetime

from app.analysis import engine, storage
from app.analysis.processor import YOLOPoseWrapper


_processor_lock = threading.Lock()
_cached_processor: Optional[YOLOPoseWrapper] = None


def get_processor() -> YOLOPoseWrapper:
    global _cached_processor
    with _processor_lock:
        if _cached_processor is None:
            model_name = os.getenv("MOVEON_YOLO_MODEL")
            _cached_processor = YOLOPoseWrapper(model=model_name)
        return _cached_processor


_executor = ThreadPoolExecutor(max_workers=int(os.getenv("MOVEON_ANALYSIS_WORKERS", "1")))


def _pending_feedback(patient_id: str, exercise_id: str, filename: str, note: str) -> Dict[str, Any]:
    return {
        "ID_Paciente": patient_id,
        "ID_Exercicio": exercise_id,
        "Timestamp": datetime.utcnow().isoformat() + "Z",
        "Status_Execucao": "Pendente",
        "Observacoes_Tecnicas": [note],
        "Repetitions": 0,
        "feedback": "A análise do vídeo está em processamento.",
        "video_filename": filename,
    }


def _error_feedback(patient_id: str, exercise_id: str, filename: str, err: str) -> Dict[str, Any]:
    return {
        "ID_Paciente": patient_id,
        "ID_Exercicio": exercise_id,
        "Timestamp": datetime.utcnow().isoformat() + "Z",
        "Status_Execucao": "Erro",
        "Observacoes_Tecnicas": [f"Analysis error: {err}"],
        "Repetitions": 0,
        "feedback": f"Erro ao processar o vídeo: {err}",
        "video_filename": filename,
    }


def analyze_and_log(patient_id: str, exercise_id: str, video_path: str, filename: str) -> Dict[str, Any]:
    """Run analysis (blocking) and write a final log entry."""
    try:
        proc = get_processor()
        feedback = engine.analyze_video(patient_id, exercise_id, video_path, processor=proc)
        if isinstance(feedback, dict):
            feedback.setdefault("video_filename", filename)
        storage.save_feedback(feedback)
        return feedback
    except NotImplementedError:
        feedback = _pending_feedback(
            patient_id,
            exercise_id,
            filename,
            "Inference unavailable in this environment; análise adiada",
        )
        storage.save_feedback(feedback)
        return feedback
    except Exception as exc:  # noqa: BLE001
        feedback = _error_feedback(patient_id, exercise_id, filename, str(exc))
        storage.save_feedback(feedback)
        return feedback


def submit_analysis(patient_id: str, exercise_id: str, video_path: str, filename: str) -> Future:
    """Submit analysis to background thread pool."""
    return _executor.submit(analyze_and_log, patient_id, exercise_id, video_path, filename)
