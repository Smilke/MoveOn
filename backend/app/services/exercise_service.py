from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.exercise_library import ExerciseLibrary
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate

class ExerciseService:
    """Serviço para gerenciar a biblioteca de exercícios"""

    @staticmethod
    def create_exercise(
        session: Session,
        exercise_data: ExerciseCreate
    ) -> ExerciseLibrary:
        """Cria um novo exercício na biblioteca"""
        try:
            # Criar o objeto ExerciseLibrary a partir dos dados validados
            exercise_dict = exercise_data.model_dump()
            exercise = ExerciseLibrary(**exercise_dict)
            
            # Adicionar à sessão
            session.add(exercise)
            
            # Fazer flush para garantir que o objeto tenha um ID
            session.flush()
            
            # Fazer commit da transação
            session.commit()
            
            # Atualizar o objeto com os dados do banco (incluindo ID e timestamps)
            session.refresh(exercise)
            
            return exercise
        except IntegrityError as e:
            session.rollback()
            raise ValueError(f"Erro de integridade ao criar exercício: {str(e)}")
        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Erro ao criar exercício no banco de dados: {str(e)}")
        except Exception as e:
            session.rollback()
            raise ValueError(f"Erro inesperado ao criar exercício: {str(e)}")

    @staticmethod
    def get_exercise(session: Session, exercise_id: int) -> Optional[ExerciseLibrary]:
        """Obtém um exercício por ID"""
        return session.get(ExerciseLibrary, exercise_id)

    @staticmethod
    def get_all_exercises(session: Session, active_only: bool = True) -> List[ExerciseLibrary]:
        """Obtém todos os exercícios da biblioteca"""
        statement = select(ExerciseLibrary)
        
        if active_only:
            statement = statement.where(ExerciseLibrary.is_active == True)
        
        return list(session.exec(statement.order_by(ExerciseLibrary.name)).all())

    @staticmethod
    def update_exercise(
        session: Session,
        exercise_id: int,
        exercise_data: ExerciseUpdate
    ) -> Optional[ExerciseLibrary]:
        """Atualiza um exercício existente"""
        try:
            exercise = session.get(ExerciseLibrary, exercise_id)
            if not exercise:
                return None
            
            update_data = exercise_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(exercise, field, value)
            
            # Atualizar o campo updated_at manualmente
            exercise.updated_at = datetime.utcnow()
            
            session.add(exercise)
            session.commit()
            session.refresh(exercise)
            
            return exercise
        except IntegrityError as e:
            session.rollback()
            raise ValueError(f"Erro de integridade ao atualizar exercício: {str(e)}")
        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Erro ao atualizar exercício no banco de dados: {str(e)}")
        except Exception as e:
            session.rollback()
            raise ValueError(f"Erro inesperado ao atualizar exercício: {str(e)}")

    @staticmethod
    def delete_exercise(session: Session, exercise_id: int) -> bool:
        """Desativa um exercício (soft delete)"""
        try:
            exercise = session.get(ExerciseLibrary, exercise_id)
            if not exercise:
                return False
            
            exercise.is_active = False
            exercise.updated_at = datetime.utcnow()
            session.add(exercise)
            session.commit()
            
            return True
        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Erro ao desativar exercício no banco de dados: {str(e)}")
        except Exception as e:
            session.rollback()
            raise ValueError(f"Erro inesperado ao desativar exercício: {str(e)}")
