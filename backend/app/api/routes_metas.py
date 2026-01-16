from __future__ import annotations
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

from app.core.database import get_session
from app.models.goal import Goal
from app.models.patient import Patient
from app.api.routes_notificacoes import router as notificacoes_router
from notificacoes import registrar_notificacao
from repositorio_memoria import repo_notificacao_memoria

router = APIRouter()

class MetaIn(BaseModel):
    patient_id: str
    physiotherapist_id: int
    description: str
    success_criteria: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class MetaOut(BaseModel):
    id: int
    patient_id: int
    physiotherapist_id: int
    description: str
    success_criteria: Optional[str] = None
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class AtualizarStatusIn(BaseModel):
    novo_status: str

@router.post("/metas", response_model=MetaOut, status_code=status.HTTP_201_CREATED)
def criar_meta(body: MetaIn, session: Session = Depends(get_session)):
    try:
        paciente = None
        try:
            pid_int = int(body.patient_id)
            paciente = session.exec(select(Patient).where((Patient.id == pid_int) | (Patient.cpf == body.patient_id))).first()
        except ValueError:
            paciente = session.exec(select(Patient).where(Patient.cpf == body.patient_id)).first()
        
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")

        # Parsing de datas
        dt_inicio = datetime.utcnow()
        if body.start_date and body.start_date.strip():
            try:
                dt_inicio = datetime.fromisoformat(body.start_date.replace('Z', '+00:00'))
            except ValueError:
                try:
                    dt_inicio = datetime.strptime(body.start_date, "%Y-%m-%d")
                except ValueError:
                    raise HTTPException(status_code=400, detail="Formato de start_date inválido")

        dt_fim = None
        if body.end_date and body.end_date.strip():
            try:
                dt_fim = datetime.fromisoformat(body.end_date.replace('Z', '+00:00'))
            except ValueError:
                try:
                    dt_fim = datetime.strptime(body.end_date, "%Y-%m-%d")
                except ValueError:
                    raise HTTPException(status_code=400, detail="Formato de end_date inválido")

        nova_meta = Goal(
            patient_id=paciente.id,
            physiotherapist_id=body.physiotherapist_id,
            description=body.description,
            success_criteria=body.success_criteria,
            status="ativa",
            start_date=dt_inicio,
            end_date=dt_fim
        )

        session.add(nova_meta)
        session.commit()
        session.refresh(nova_meta)

        # Notificação de nova meta
        try:
            registrar_notificacao(
                repo_notificacao_memoria,
                paciente_id=str(paciente.id),
                tipo="nova_meta",
                mensagem=f"Seu fisioterapeuta definiu uma nova meta para você: {nova_meta.description}."
            )
        except Exception as e_notif:
            print(f"Erro ao registrar notificação de nova meta: {e_notif}")

        return nova_meta
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao criar meta: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/pacientes/{paciente_id}/metas", response_model=List[MetaOut])
def listar_metas_paciente(paciente_id: str, session: Session = Depends(get_session)):
    try:
        paciente = None
        try:
            pid_int = int(paciente_id)
            paciente = session.exec(select(Patient).where((Patient.id == pid_int) | (Patient.cpf == paciente_id))).first()
        except ValueError:
            paciente = session.exec(select(Patient).where(Patient.cpf == paciente_id)).first()
        
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")

        statement = select(Goal).where(Goal.patient_id == paciente.id)
        metas = session.exec(statement).all()
        return metas
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao listar metas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/metas/{meta_id}/status")
def atualizar_status(meta_id: int, body: AtualizarStatusIn, session: Session = Depends(get_session)):
    try:
        meta = session.get(Goal, meta_id)
        if not meta:
            raise HTTPException(status_code=404, detail="Meta não encontrada")

        status_validos = {"ativa", "em_andamento", "concluida", "nao_atingida"}
        if body.novo_status not in status_validos:
            raise HTTPException(status_code=400, detail="Status inválido")

        meta.status = body.novo_status
        session.add(meta)
        session.commit()
        session.refresh(meta)

        # Notificação
        try:
            mensagem = (
                f"Sua meta '{meta.description}' "
                f"agora está com status '{meta.status}'."
            )

            registrar_notificacao(
                repo_notificacao_memoria,
                paciente_id=str(meta.patient_id),
                tipo="status_meta_atualizado",
                mensagem=mensagem,
            )
        except Exception as e_notif:
            print(f"Erro ao registrar notificação: {e_notif}")

        return {"mensagem": "Status da meta atualizado com sucesso", "status": meta.status}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao atualizar status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
