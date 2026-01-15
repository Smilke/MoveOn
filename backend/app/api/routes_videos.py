from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()


@router.get("/videos/{filename}", summary="Baixa/serve um vídeo enviado")
def get_uploaded_video(filename: str):
    # Evitar path traversal
    if not filename or "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")

    base_dir = Path(__file__).resolve().parents[1]  # backend/app
    uploads_dir = base_dir / "uploads"
    file_path = uploads_dir / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    return FileResponse(path=str(file_path), filename=filename)
