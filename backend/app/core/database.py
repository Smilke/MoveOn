from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# Importar todos os models para que sejam registrados no SQLModel.metadata
from app.models import (
    Patient,
    Physiotherapist,
    ExerciseLibrary,
    Prescription,
    ExerciseExecution,
    PainLevel,
    Feedback,
    PrescriptionHistory,
)

# Criar engine do banco de dados
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Log SQL queries (pode desabilitar em produção)
    pool_pre_ping=True,  # Verifica conexões antes de usar
)


def init_db():
    """Cria todas as tabelas no banco de dados"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency para obter sessão do banco de dados"""
    with Session(engine) as session:
        yield session