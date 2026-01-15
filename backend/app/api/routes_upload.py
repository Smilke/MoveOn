from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid

from app.analysis import engine
from app.analysis import processor as processor_mod
from app.analysis import storage

router = APIRouter()


@router.post("/upload/video", summary="Faz upload de um vídeo")
async def upload_video(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    exercise_id: str = Form(...),
):
    try:
        base_dir = Path(__file__).resolve().parents[1]
        upload_dir = base_dir / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        ext = Path(file.filename).suffix if file.filename else ""
        filename = f"{uuid.uuid4().hex}{ext}"
        dest = upload_dir / filename

        content = await file.read()
        with dest.open("wb") as f:
            f.write(content)

        # attempt analysis
        feedback = None
        try:
            proc = processor_mod.YOLOPoseWrapper()
            # engine.analyze_video may raise NotImplementedError if model not available
            feedback = engine.analyze_video(patient_id, exercise_id, str(dest), processor=proc)
        except NotImplementedError:
            # fallback feedback when inference unavailable in this environment
            feedback = {
                "ID_Paciente": patient_id,
                "ID_Exercicio": exercise_id,
                "Timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                "Status_Execucao": "Pendente",
                "Observacoes_Tecnicas": ["Inference unavailable in this environment; análise adiada"],
                "Repetitions": 0,
                "feedback": "O vídeo foi recebido, mas a análise automática não está disponível neste ambiente.",
            }
        except Exception as exc:
            feedback = {
                "ID_Paciente": patient_id,
                "ID_Exercicio": exercise_id,
                "Timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                "Status_Execucao": "Erro",
                "Observacoes_Tecnicas": [f"Analysis error: {str(exc)}"],
                "Repetitions": 0,
                "feedback": f"Erro ao processar o vídeo: {str(exc)}",
            }

        # garantir que o log tenha referência ao arquivo enviado
        try:
            if isinstance(feedback, dict):
                feedback.setdefault("video_filename", filename)
        except Exception:
            pass

        # persist feedback/log
        try:
            storage.save_feedback(feedback)
        except Exception:
            # non-fatal
            pass

        return JSONResponse(status_code=201, content={"filename": filename, "saved_path": str(dest), "analysis": feedback})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
