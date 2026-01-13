from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from cadastro_meta import cadastrar_meta, atualizar_status_meta
from repositorio_memoria import RepositorioMetaMemoria
from repositorio_memoria import RepositorioNotificacaoMemoria
from notificacoes import registrar_notificacao


router = APIRouter()

repo_metas = RepositorioMetaMemoria()

repo_notificacoes = RepositorioNotificacaoMemoria()



class MetaIn(BaseModel):
    paciente_id: str
    fisioterapeuta_id: str
    descricao: str
    criterio_sucesso: str | None = None
    data_inicio: str
    data_fim: str


class AtualizarStatusIn(BaseModel):
    novo_status: str


@router.post("/metas", status_code=status.HTTP_201_CREATED)
def criar_meta(body: MetaIn):
    dados = body.dict()
    erros = cadastrar_meta(dados, repo_metas)

    if erros:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=erros,
        )

    return {"mensagem": "Meta cadastrada com sucesso"}


@router.get("/pacientes/{paciente_id}/metas")
def listar_metas_ativas_paciente(paciente_id: str):
    metas = repo_metas.listar_ativas_por_paciente(paciente_id)
    return metas



@router.patch("/metas/{meta_id}/status")
def atualizar_status(meta_id: int, body: AtualizarStatusIn):
    erros = atualizar_status_meta(meta_id, body.novo_status, repo_metas)
    if erros:
        raise HTTPException(status_code=400, detail=erros)

    # pega a meta atualizada no repositório
    meta = repo_metas.obter_por_id(meta_id)
    if meta:
        mensagem = (
            f"Sua meta '{meta.get('descricao', '')}' "
            f"agora está com status '{meta.get('status', '')}'."
        )

        registrar_notificacao(
            repo_notificacoes,
            paciente_id=meta.get("paciente_id"),
            tipo="status_meta_atualizado",
            mensagem=mensagem,
        )

    return {"mensagem": "Status da meta atualizado com sucesso."}
