from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.api.routes_health import router as health_router
from app.api.routes_prescriptions import router as prescriptions_router
from app.api.routes_exercises import router as exercises_router
from app.api.routes_reports import router as reports_router
from app.api.routes_progress_report import router as progress_reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas do banco de dados ao iniciar
    create_db_and_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

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

    app.include_router(
        health_router,
        prefix=api_prefix,
        tags=["health"],
    )

    app.include_router(
        exercises_router,
        prefix=api_prefix,
        tags=["exercises"]
    )

    app.include_router(
        prescriptions_router,
        prefix=api_prefix,
        tags=["prescriptions"]
    )

    app.include_router(
        reports_router,
        prefix=api_prefix,
        tags=["reports"]
    )
    
    app.include_router(
        progress_reports_router,
        prefix=api_prefix,
        tags=["progress-reports"]
    )

    @app.get("/")
    def root():
        return {"message": "API rodando", "project": settings.PROJECT_NAME}

    return app


app = create_app()
