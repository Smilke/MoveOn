from sqlmodel import Session, select
from app.core.database import engine
from app.models.patient import Patient

with Session(engine) as session:
    patients = session.exec(select(Patient)).all()
    print(f"Found {len(patients)} patients")
    for p in patients:
        print({
            'id': p.id,
            'name': getattr(p,'name',None),
            'email': p.email,
            'cpf': getattr(p,'cpf',None)
        })
