from sqlmodel import Session
from app.core.database import engine
from app.api.routes_login import login, LoginIn

with Session(engine) as session:
    body = LoginIn(email='paciente@moveon.com', senha='Senha124')
    try:
        out = login(body, session=session)
        print(out.model_dump())
    except Exception as e:
        print('ERROR:', type(e).__name__, e)
