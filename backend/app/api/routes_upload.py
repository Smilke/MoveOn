from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
from datetime import datetime

from app.analysis import engine
from app.analysis import storage
from app.analysis import runtime

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

        # 1) Log imediato como "Pendente" (assim UI pode mostrar aguardando)
        pending = {
            "ID_Paciente": patient_id,
            "ID_Exercicio": exercise_id,
            "Timestamp": datetime.utcnow().isoformat() + "Z",
            "Status_Execucao": "Pendente",
            "Observacoes_Tecnicas": ["Vídeo recebido; análise em processamento"],
            "Repetitions": 0,
            "feedback": "A análise do vídeo está em processamento.",
            "video_filename": filename,
            "progress": 0,
        }
        try:
            storage.save_feedback(pending)
        except Exception:
            pass

        # 2) Rodar análise em segundo plano (não bloqueia a resposta)
        try:
            runtime.submit_analysis(patient_id, exercise_id, str(dest), filename)
        except Exception:
            # se falhar enfileirar, não derruba upload
            pass

        return JSONResponse(status_code=201, content={"filename": filename, "saved_path": str(dest), "analysis": pending})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
