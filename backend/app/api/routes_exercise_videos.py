from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()


def _exercise_videos_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "uploads" / "exercise_example_videos"


@router.get(
    "/exercise-videos/{filename}",
    summary="Serve vídeo de exemplo de exercício",
)
def get_exercise_video(filename: str):
    if not filename or "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")

    video_path = _exercise_videos_dir() / filename
    if not video_path.exists() or not video_path.is_file():
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")

    return FileResponse(str(video_path))
