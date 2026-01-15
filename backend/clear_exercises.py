from sqlmodel import Session, delete
from app.core.database import engine
from app.models.exercise_library import ExerciseLibrary
from app.models.prescription import Prescription
from app.models.exercise_execution import ExerciseExecution
from app.models.feedback import Feedback
from app.models.pain_level import PainLevel

def clear_exercises():
    print("Iniciando limpeza de exercícios e dados relacionados...")
    with Session(engine) as session:
        try:
            # Deletar em ordem de dependência (filhos primeiro)
            print("- Removendo Feedbacks...")
            session.exec(delete(Feedback))
            
            print("- Removendo Níveis de Dor...")
            session.exec(delete(PainLevel))
            
            print("- Removendo Execuções de Exercícios...")
            session.exec(delete(ExerciseExecution))
            
            print("- Removendo Prescrições...")
            session.exec(delete(Prescription))
            
            print("- Removendo Biblioteca de Exercícios...")
            session.exec(delete(ExerciseLibrary))
            
            session.commit()
            print("\n✅ Sucesso! A lista de exercícios está limpa.")
        except Exception as e:
            session.rollback()
            print(f"\n❌ Erro ao limpar dados: {e}")

if __name__ == "__main__":
    clear_exercises()
