from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes_health import router as health_router
from app.api.routes_fisioterapeuta import router as fisioterapeuta_router  
from app.api.routes_paciente import router as paciente_router
from app.api.routes_notificacoes import router as notificacoes_router
from app.api.routes_metas import router as metas_router
from app.api.routes_login import router as login_router
from app.api.routes_recuperacao_senha import router as recuperacao_router
from app.api.routes_feedback import router as feedback_router
from app.api.routes_prescricoes import router as prescricoes_router  

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
    
    api_prefix = settings.API_PREFIX  

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


    app.include_router(
        paciente_router,
        prefix=api_prefix,
        tags=["pacientes"],
    )

    app.include_router(
        notificacoes_router,
        prefix=api_prefix,
        tags=["notificacoes"],
    )


    app.include_router(
        metas_router,
        prefix=api_prefix,
        tags=["metas"],
    )

    app.include_router(
        login_router,
        prefix=api_prefix,
        tags=["login"],
)
    app.include_router(
        recuperacao_router,
        prefix=api_prefix,
        tags=["recuperacao_senha"],
)

    app.include_router(
        feedback_router,
        prefix=api_prefix,
        tags=["feedbacks"],
)


    app.include_router(      
        prescricoes_router,
        prefix=api_prefix,
        tags=["prescricoes"],
    )

    return app


app = create_app()
