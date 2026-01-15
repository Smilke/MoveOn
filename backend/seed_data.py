from app.core.database import engine, create_db_and_tables
from sqlmodel import Session, select
from app.models.physiotherapist import Physiotherapist

def seed():
    create_db_and_tables()
    with Session(engine) as session:
        # Check if exists
        statement = select(Physiotherapist).where(Physiotherapist.email == "admin@moveon.com")
        existing = session.exec(statement).first()
        
        if not existing:
            print("Creating default physiotherapist...")
            fisio = Physiotherapist(
                name="Fisio Admin",
                email="admin@moveon.com",
                cpf="00000000000",
                license_number="12345-F"
            )
            session.add(fisio)
            session.commit()
            print("Done! Login with: admin@moveon.com / Senha124")
        else:
            print("Physiotherapist already exists.")
            fisio = existing

        # Seed Patient
        from app.models.patient import Patient
        stmt_pat = select(Patient).where(Patient.email == "paciente@moveon.com")
        patient = session.exec(stmt_pat).first()
        if not patient:
            print("Creating default patient...")
            patient = Patient(name="Paciente Teste", email="paciente@moveon.com", cpf="12345678901")
            session.add(patient)
            session.commit()
            print("Done! Patient login: paciente@moveon.com / (Login with email only)")
        
        # Seed Exercise
        from app.models.exercise_library import ExerciseLibrary
        from app.models.exercise_library import DifficultyLevel
        stmt_ex = select(ExerciseLibrary).where(ExerciseLibrary.name == "Alongamento Matinal")
        exercise = session.exec(stmt_ex).first()
        if not exercise:
            print("Creating default exercise...")
            exercise = ExerciseLibrary(
                name="Alongamento Matinal", 
                description="Alongamento leve para começar o dia", 
                category="Flexibilidade",
                difficulty=DifficultyLevel.BEGINNER
            )
            session.add(exercise)
            session.commit()
        
        # Seed Prescription
        from app.models.prescription import Prescription
        # Check if patient has this exercise prescribed
        stmt_presc = select(Prescription).where(
            (Prescription.patient_id == patient.id) & 
            (Prescription.exercise_id == exercise.id)
        )
        presc = session.exec(stmt_presc).first()
        if not presc:
            print("Creating default prescription...")
            presc = Prescription(
                patient_id=patient.id,
                physiotherapist_id=fisio.id,
                exercise_id=exercise.id,
                repetitions=10,
                series=3,
                notes="Fazer com calma."
            )
            session.add(presc)
            session.commit()
            print("Prescription created!")

if __name__ == "__main__":
    seed()
