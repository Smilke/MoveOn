from contextlib import asynccontextmanager
# backend/app/main.py
from fastapi import FastAPI
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db  # <<< IMPORTANTE

from app.api.routes_health import router as health_router
from app.api.routes_fisioterapeuta import router as fisioterapeuta_router
from app.api.routes_paciente import router as paciente_router
from app.api.routes_notificacoes import router as notificacoes_router
from app.api.routes_metas import router as metas_router
from app.api.routes_login import router as login_router
from app.api.routes_recuperacao_senha import router as recuperacao_router
from app.api.routes_feedback import router as feedback_router
from app.api.routes_exercises import router as exercises_router
from app.api.routes_execution_history import router as execution_history_router
from app.api.routes_prescriptions import router as prescriptions_router
from app.api.routes_patients import router as patients_router
from app.api.routes_reports import router as reports_router
from app.api.routes_progress_report import router as progress_reports_router
from app.api.routes_patients_db import router as patients_db_router
from app.api.routes_fisioterapeuta_db import router as fisioterapeuta_db_router
from app.api.routes_upload import router as upload_router
from app.api.routes_videos import router as videos_router
from app.api.routes_exercise_videos import router as exercise_videos_router
from app.api.routes_execution_feedback import router as execution_feedback_router


def create_app() -> FastAPI:
    from app.api.routes_video_feedback import router as video_feedback_router
    app = FastAPI(title=settings.PROJECT_NAME)

    origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5500",  # Common for VS Code Live Server
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_prefix = settings.API_PREFIX

    # rota raiz só pra sanity check
    @app.get("/")
    def root():
        return {"message": "API rodando", "project": settings.PROJECT_NAME}

    # health
    app.include_router(health_router, prefix=api_prefix, tags=["health"])

    # login
    app.include_router(login_router, prefix=api_prefix, tags=["login"])

    # pacientes
    app.include_router(patients_router, prefix=api_prefix, tags=["patients"])
    # feedbacks de vídeo
    app.include_router(video_feedback_router, prefix=api_prefix, tags=["video-feedbacks"])

    # upload de vídeo
    app.include_router(upload_router, prefix=api_prefix, tags=["upload"])

    # servir vídeos enviados
    app.include_router(videos_router, prefix=api_prefix, tags=["videos"])

    # servir vídeos de exemplo de exercícios
    app.include_router(exercise_videos_router, prefix=api_prefix, tags=["exercise-videos"])
    
    # exercícios e prescrições
    app.include_router(exercises_router, prefix=api_prefix, tags=["exercises"])
    app.include_router(prescriptions_router, prefix=api_prefix, tags=["prescriptions"])
    app.include_router(execution_history_router, prefix=api_prefix, tags=["execution_history"])

    # relatórios
    app.include_router(reports_router, prefix=api_prefix, tags=["reports"])
    app.include_router(progress_reports_router, prefix=api_prefix, tags=["progress-reports"])

    # feedback do fisioterapeuta por execução
    app.include_router(execution_feedback_router, prefix=api_prefix, tags=["execution-feedbacks"])


    # outros
    app.include_router(fisioterapeuta_router, prefix=api_prefix, tags=["fisioterapeutas"])
    app.include_router(notificacoes_router, prefix=api_prefix, tags=["notificacoes"])
    app.include_router(metas_router, prefix=api_prefix, tags=["metas"])
    app.include_router(recuperacao_router, prefix=api_prefix, tags=["recuperacao_senha"])
    app.include_router(feedback_router, prefix=api_prefix, tags=["feedbacks"])

    # Legacy/Other DB routers
    app.include_router(patients_db_router, prefix=api_prefix, tags=["patients_db"])
    app.include_router(fisioterapeuta_db_router, prefix=api_prefix, tags=["fisioterapeutas_db"])
    
    @app.on_event("startup")
    def on_startup() -> None:
        # cria todas as tabelas definidas em app.models
        init_db()

    return app

app = create_app()