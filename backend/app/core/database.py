from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
from app.models import patient, physiotherapist, exercise_library, prescription, exercise_execution, pain_level, feedback

# Url de conexão com o banco de dados
# Se não estiver definido em settings, usa um arquivo local por padrão
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
    
    SQLModel.metadata.create_all(engine)
