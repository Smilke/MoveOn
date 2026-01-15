
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from typing import List, Dict, Any
from sqlmodel import Session, select
from app.core.database import engine
from app.models.exercise_library import ExerciseLibrary
from app.models.patient import Patient

router = APIRouter()


def _load_video_feedbacks_for_patient(patient_id: int) -> List[Dict[str, Any]]:
    # Este módulo fica em backend/app/api; o log fica em backend/app/uploads
    logs_path = Path(__file__).resolve().parents[1] / "uploads" / "analysis_logs.jsonl"
    if not logs_path.exists():
        return []

    # Carregar todos os exercícios em memória para mapear id->nome
    exercise_map: Dict[str, str] = {}
    with Session(engine) as session:
        for ex in session.exec(select(ExerciseLibrary)).all():
            exercise_map[str(ex.id)] = ex.name

    feedbacks: List[Dict[str, Any]] = []
    with logs_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                pid = entry.get("ID_Paciente") or entry.get("patient_id")
                if str(pid) != str(patient_id):
                    continue

                ex_id = entry.get("ID_Exercicio") or entry.get("exercise_id")
                detalhes = entry.get("rep_details")
                if detalhes is None and "Rep_Details" in entry:
                    detalhes = entry["Rep_Details"]

                video_filename = entry.get("video_filename") or entry.get("filename")

                feedbacks.append(
                    {
                        "exercise_id": ex_id,
                        "exercise_name": exercise_map.get(str(ex_id), "Exercício"),
                        "timestamp": entry.get("Timestamp")
                        or entry.get("date")
                        or entry.get("created_at"),
                        "status": entry.get("Status_Execucao", ""),
                        "observacoes": entry.get("Observacoes_Tecnicas", []),
                        "repeticoes": entry.get("Repetitions", None),
                        "feedback": entry.get("feedback", entry.get("result", "")),
                        "detalhes": detalhes,
                        "video_filename": video_filename,
                        "video_url": f"/api/videos/{video_filename}" if video_filename else None,
                    }
                )
            except Exception:
                continue

    return feedbacks

@router.get("/patients/{patient_id}/video-feedbacks", summary="Lista feedbacks de vídeos analisados do paciente")
def get_video_feedbacks(patient_id: int):
    return _load_video_feedbacks_for_patient(patient_id)


@router.get(
    "/physiotherapists/{physio_id}/patients/{patient_id}/video-feedbacks",
    summary="Lista feedbacks de vídeos do paciente (acesso do fisioterapeuta)",
)
def get_video_feedbacks_for_physio(physio_id: int, patient_id: int):
    # Autorização simples: paciente deve estar vinculado ao fisioterapeuta
    with Session(engine) as session:
        patient = session.get(Patient, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        if patient.physiotherapist_id != physio_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

    return _load_video_feedbacks_for_patient(patient_id)