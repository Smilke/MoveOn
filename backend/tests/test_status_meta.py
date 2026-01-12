import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cadastro_meta import atualizar_status_meta


class FakeRepositorioMeta:
    def __init__(self, metas_iniciais=None):
        self.metas = metas_iniciais or []

    def obter_por_id(self, meta_id: int):
        for m in self.metas:
            if m.get("id") == meta_id:
                return m
        return None


def test_deve_atualizar_status_para_concluida():
    repo = FakeRepositorioMeta(
        metas_iniciais=[
            {"id": 1, "status": "ativa", "descricao": "Meta de teste"},
        ]
    )

    erros = atualizar_status_meta(1, "concluida", repo)

    assert erros == []
    assert repo.metas[0]["status"] == "concluida"


def test_deve_atualizar_status_para_em_andamento():
    repo = FakeRepositorioMeta(
        metas_iniciais=[
            {"id": 1, "status": "ativa", "descricao": "Meta de teste"},
        ]
    )

    erros = atualizar_status_meta(1, "em_andamento", repo)

    assert erros == []
    assert repo.metas[0]["status"] == "em_andamento"


def test_nao_deve_aceitar_status_invalido():
    repo = FakeRepositorioMeta(
        metas_iniciais=[
            {"id": 1, "status": "ativa", "descricao": "Meta de teste"},
        ]
    )

    erros = atualizar_status_meta(1, "qualquer_coisa", repo)

    assert "Status inválido." in erros
    assert repo.metas[0]["status"] == "ativa"


def test_nao_deve_atualizar_quando_meta_nao_existir():
    repo = FakeRepositorioMeta(
        metas_iniciais=[
            {"id": 1, "status": "ativa", "descricao": "Meta de teste"},
        ]
    )

    erros = atualizar_status_meta(999, "concluida", repo)

    assert "Meta não encontrada." in erros
    assert repo.metas[0]["status"] == "ativa"
