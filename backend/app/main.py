# backend/app/main.py
from fastapi import FastAPI
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
from app.api.routes_patients_db import router as patients_db_router
from app.api.routes_fisioterapeuta_db import router as fisioterapeuta_db_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)

    origins = [
        "http://localhost:5173",
        "http://localhost:3000",
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
    app.include_router(
        health_router,
        prefix=api_prefix,
        tags=["health"],
    )

    # fisioterapeutas
    app.include_router(
        fisioterapeuta_router,
        prefix=api_prefix,
        tags=["fisioterapeutas"],
    )

    # pacientes
    app.include_router(
        patients_db_router,
        prefix=api_prefix,
        tags=["pacientes"],
    )

    # notificações
    app.include_router(
        notificacoes_router,
        prefix=api_prefix,
        tags=["notificacoes"],
    )

    # metas
    app.include_router(
        metas_router,
        prefix=api_prefix,
        tags=["metas"],
    )

    # login
    app.include_router(
        login_router,
        prefix=api_prefix,
        tags=["login"],
    )

    # recuperação de senha
    app.include_router(
        recuperacao_router,
        prefix=api_prefix,
        tags=["recuperacao_senha"],
    )

    # feedback
    app.include_router(
        feedback_router,
        prefix=api_prefix,
        tags=["feedbacks"],
    )

    # exercícios gamificados (PB08)
    app.include_router(
        exercises_router,
        prefix=api_prefix,
        tags=["exercises"],
    )

    app.include_router(
        execution_history_router,
        prefix=api_prefix,
        tags=["execution_history"],  
    )

    app.include_router(
        prescriptions_router,
        prefix=api_prefix,
        tags=["prescriptions"],
    )

    app.include_router(
        patients_db_router,
        prefix=api_prefix,
        tags=["patients_db"],   
    )
    
    app.include_router(
        fisioterapeuta_db_router,
        prefix=api_prefix,
        tags=["fisioterapeutas_db"],
    )
    
    
    @app.on_event("startup")
    def on_startup() -> None:
        # cria todas as tabelas definidas em app.models
        init_db()

    return app


app = create_app()