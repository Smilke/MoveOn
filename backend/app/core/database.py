from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
from app.models import patient, physiotherapist, exercise_library, prescription, exercise_execution, pain_level, feedback, goal
from sqlalchemy import text

from app.core.security import hash_password

# Configuração do banco de dados
DATABASE_URL = getattr(settings, "DATABASE_URL", "sqlite:///./moveon_v3.db")

# Para SQLite é necessário connect_args={"check_same_thread": False}
engine = create_engine(
    DATABASE_URL, 
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

def get_session():
    """Dependência para obter uma sessão do banco de dados"""
    with Session(engine) as session:
        yield session

def init_db():
    from app.core.database import create_db_and_tables
    create_db_and_tables()

def create_db_and_tables():
    """Cria as tabelas do banco de dados"""
    # Importar modelos aqui para garantir que eles sejam registrados no SQLModel.metadata
    from app.models.patient import Patient
    from app.models.physiotherapist import Physiotherapist
    from app.models.exercise_library import ExerciseLibrary
    from app.models.exercise_example_video import ExerciseExampleVideo
    from app.models.prescription import Prescription
    from app.models.exercise_execution import ExerciseExecution
    from app.models.feedback import Feedback
    from app.models.pain_level import PainLevel
    from app.models.goal import Goal
    
    SQLModel.metadata.create_all(engine)

    # Lightweight migration for SQLite (create_all does not add columns)
    if "sqlite" in DATABASE_URL:
        with engine.begin() as conn:
            def has_column(table: str, col: str) -> bool:
                rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
                return any(r[1] == col for r in rows)

            def add_column(table: str, col_sql: str) -> None:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_sql}"))

            # patients
            if not has_column("patients", "password_hash"):
                add_column("patients", "password_hash VARCHAR(255)")
            if not has_column("patients", "must_change_password"):
                add_column("patients", "must_change_password BOOLEAN DEFAULT 1")
            if not has_column("patients", "password_reset_token_hash"):
                add_column("patients", "password_reset_token_hash VARCHAR(64)")
            if not has_column("patients", "password_reset_expires_at"):
                add_column("patients", "password_reset_expires_at DATETIME")

            # physiotherapists
            if not has_column("physiotherapists", "password_hash"):
                add_column("physiotherapists", "password_hash VARCHAR(255)")
            if not has_column("physiotherapists", "must_change_password"):
                add_column("physiotherapists", "must_change_password BOOLEAN DEFAULT 0")
            if not has_column("physiotherapists", "password_reset_token_hash"):
                add_column("physiotherapists", "password_reset_token_hash VARCHAR(64)")
            if not has_column("physiotherapists", "password_reset_expires_at"):
                add_column("physiotherapists", "password_reset_expires_at DATETIME")

            # Backfill default passwords where missing
            default_patient_hash = hash_password(settings.DEFAULT_PATIENT_PASSWORD)
            default_physio_hash = hash_password(settings.DEFAULT_PHYSIO_PASSWORD)
            conn.execute(
                text(
                    "UPDATE patients SET password_hash = :h, must_change_password = 1 "
                    "WHERE password_hash IS NULL"
                ),
                {"h": default_patient_hash},
            )
            conn.execute(
                text(
                    "UPDATE physiotherapists SET password_hash = :h "
                    "WHERE password_hash IS NULL"
                ),
                {"h": default_physio_hash},
            )
