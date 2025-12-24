import sys
from pathlib import Path
from datetime import datetime

# deixa o Python enxergar a pasta backend/
sys.path.insert(0, str(Path(__file__).parent.parent))

from cadastro_feedback import cadastrar_feedback


class FakeRepositorioFeedback:
    def __init__(self):
        self.salvou = False
        self.ultimo_registro = None
        self.todos = []

    def salvar(self, dados): 
        self.salvou = True
        self.ultimo_registro = dados
        self.todos.append(dados)

def test_deve_salvar_feedback_quando_dados_validos():

    repo = FakeRepositorioFeedback()

    dados = {
        "paciente_id": "12345678901",
        "fisioterapeuta_id": "11122233344",
        "mensagem": "Senti um pouco de dor, mas consegui fazer os exercícios.",
        "avaliacao": 4,

    }

    erros = cadastrar_feedback(dados, repo)

    assert erros == []
    assert repo.salvou is True
    assert "data_hora" in repo.ultimo_registro

def test_nao_deve_salvar_quando_validacao_retornar_erros():

    repo = FakeRepositorioFeedback()

    dados = {
        "paciente_id": "12345678901",
        "fisioterapeuta_id": "11122233344",
        "mensagem": "",
        "avaliacao": 6,
    }

    erros = cadastrar_feedback(dados, repo)

    assert "Mensagem é obrigatória." in erros
    assert repo.salvou is False
    assert repo.ultimo_registro is None