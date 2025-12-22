from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes_health import router as health_router
from app.api.routes_fisioterapeuta import router as fisioterapeuta_router  
from app.api.routes_fisioterapeuta import router as fisio_router


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

    @app.get("/")
    def root():
        return {"message": "API rodando", "project": settings.PROJECT_NAME}
    
    api_prefix = settings.API_PREFIX  # normalmente é "/api"

    app.include_router(
        health_router,
        prefix=api_prefix,
        tags=["health"],
    )

    app.include_router(
        fisioterapeuta_router,
        prefix=api_prefix,
        tags=["fisioterapeutas"],
    )


    return app


app = create_app()
