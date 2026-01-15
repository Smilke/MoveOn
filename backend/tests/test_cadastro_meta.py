import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cadastro_meta import cadastrar_meta


class FakeRepositorioMeta:
    def __init__(self):
        self.salvou = False
        self.metas = []
        self.ultima_meta = None
        self._proximo_id = 1

    def salvar(self, meta):
        meta_com_id = meta.copy()
        meta_com_id["id"] = self._proximo_id
        self._proximo_id += 1

        self.salvou = True
        self.ultima_meta = meta_com_id
        self.metas.append(meta_com_id)


def test_deve_salvar_meta_quando_dados_validos():
    repo = FakeRepositorioMeta()

    dados = {
        "paciente_id": "12345678901",
        "fisioterapeuta_id": "11122233344",
        "descricao": "Reduzir dor média para <= 3 em 4 semanas.",
        "criterio_sucesso": "Paciente relata dor média <= 3 por 7 dias seguidos.",
        "data_inicio": "2025-01-01",
        "data_fim": "2025-01-31",
    }

    erros = cadastrar_meta(dados, repo)

    assert erros == []

    assert repo.salvou is True
    assert repo.ultima_meta is not None

    assert "id" in repo.ultima_meta
    assert repo.ultima_meta["status"] == "ativa"

    assert repo.ultima_meta["paciente_id"] == "12345678901"
    assert repo.ultima_meta["fisioterapeuta_id"] == "11122233344"
    assert repo.ultima_meta["descricao"].startswith("Reduzir dor")


def test_nao_deve_salvar_meta_quando_invalidos():
    repo = FakeRepositorioMeta()

    dados = {
        "paciente_id": "",  # inválido
        "fisioterapeuta_id": "11122233344",
        "descricao": "",
        "criterio_sucesso": "Paciente registra 5 sessões por semana.",
        "data_inicio": "",
        "data_fim": "",
    }

    erros = cadastrar_meta(dados, repo)

    assert "ID do paciente é obrigatório." in erros
    assert "Descrição da meta é obrigatória." in erros

    assert repo.salvou is False
    assert repo.ultima_meta is None
    assert repo.metas == []
