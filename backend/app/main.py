from fastapi import FastAPI
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes_health import router as health_router
from app.api.routes_upload import router as upload_router


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

    app.include_router(
        health_router,
        prefix=api_prefix,
        tags=["health"],
    )

    # serve uploaded files under /api/uploads
    base_dir = Path(__file__).resolve().parents[1]
    upload_dir = base_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount(f"{api_prefix}/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

    app.include_router(
        upload_router,
        prefix=api_prefix,
        tags=["upload"],
    )

    @app.get("/")
    def root():
        return {"message": "API rodando", "project": settings.PROJECT_NAME}

    return app


app = create_app()
