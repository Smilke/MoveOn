from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.core.database import get_session
from app.schemas.physiotherapist import (
    PhysiotherapistCreate,
    PhysiotherapistResponse,
)
from app.services.physiotherapist_service import PhysiotherapistService

router = APIRouter()


@router.post(
    "/fisioterapeutas-db",
    response_model=PhysiotherapistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar fisioterapeuta no banco de dados",
    description="Cria um novo fisioterapeuta na tabela physiotherapists."
)
def create_physiotherapist(
    body: PhysiotherapistCreate,
    session: Session = Depends(get_session),
):
    try:
        physio = PhysiotherapistService.create_physiotherapist(session, body)
        return physio
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar fisioterapeuta: {str(e)}",
        )


@router.get(
    "/fisioterapeutas-db",
    response_model=List[PhysiotherapistResponse],
    summary="Listar fisioterapeutas do banco",
    description="Retorna todos os fisioterapeutas cadastrados na tabela physiotherapists."
)
def list_physiotherapists(
    session: Session = Depends(get_session),
):
    physios = PhysiotherapistService.list_all(session)
    return physios


@router.get(
    "/fisioterapeutas-db/{physio_id}",
    response_model=PhysiotherapistResponse,
    summary="Consultar fisioterapeuta por ID",
    description="Retorna os dados de um fisioterapeuta específico pelo ID do banco."
)
def get_physiotherapist(
    physio_id: int,
    session: Session = Depends(get_session),
):
    physio = PhysiotherapistService.get_by_id(session, physio_id)
    if not physio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fisioterapeuta não encontrado.",
        )
    return physio