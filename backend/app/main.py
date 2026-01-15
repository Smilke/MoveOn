from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.routes_health import router as health_router
from app.api.routes_prescriptions import router as prescriptions_router
from app.api.routes_reports import router as reports_router
from app.api.routes_exercises import router as exercises_router
from app.api.routes_execution_history import router as execution_history_router
from app.api.routes_progress_report import router as progress_report_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Sistema de acompanhamento remoto de pacientes em reabilitação para fisioterapeutas",
        version="1.0.0",
    )

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

    app.include_router(
        health_router,
        prefix=api_prefix,
        tags=["health"],
    )
    
    app.include_router(
        prescriptions_router,
        prefix=api_prefix,
        tags=["prescriptions"],
    )
    
    app.include_router(
        exercises_router,
        prefix=api_prefix,
        tags=["exercises"],
    )
    
    app.include_router(
        execution_history_router,
        prefix=api_prefix,
        tags=["execution-history"],
    )
    
    app.include_router(
        progress_report_router,
        prefix=api_prefix,
        tags=["progress-report"],
    )
    
    app.include_router(
        reports_router,
        prefix=api_prefix,
        tags=["reports"],
    )

    @app.on_event("startup")
    def on_startup():
        """Inicializa o banco de dados na inicialização da aplicação"""
        init_db()

    @app.get("/")
    def root():
        return {"message": "API rodando", "project": settings.PROJECT_NAME}

    return app


app = create_app()