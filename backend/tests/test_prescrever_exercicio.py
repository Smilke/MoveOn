# tests/test_prescrever_exercicio.py

import sys
from pathlib import Path

# permite importar o use case a partir da pasta backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from prescrever_exercicio import prescrever_exercicio


class FakeRepositorioExercicios:
    def __init__(self, exercicios=None):
        # lista de dicts, ex.: {"id": 1, "nome": "...", "nivel_dificuldade": "Médio"}
        self._exercicios = exercicios or []

    def esta_vazia(self) -> bool:
        return len(self._exercicios) == 0

    def obter_por_id(self, exercicio_id: int):
        for e in self._exercicios:
            if e.get("id") == exercicio_id:
                return e
        return None


class FakeRepositorioPrescricoes:
    def __init__(self):
        self._prescricoes = []
        self.salvou = False
        self.ultima_prescricao = None

    def proximo_id(self) -> int:
        return len(self._prescricoes) + 1

    def salvar(self, prescricao: dict) -> None:
        self.salvou = True
        self.ultima_prescricao = prescricao
        self._prescricoes.append(prescricao)

    def listar_por_paciente(self, paciente_id: str):
        return [p for p in self._prescricoes if p["paciente_id"] == paciente_id]


def test_prescricao_bem_sucedida_de_exercicio_gamificado():
    """
    Cenário do doc:
    - Fisio seleciona "Agachamento Gamificado"
    - Define 3 séries, 10 repetições, duração 15 min, 5x por semana
    - Deve exibir "Exercício prescrito com sucesso"
    - E o exercício deve aparecer na lista do paciente
    """
    repo_exercicios = FakeRepositorioExercicios(
        exercicios=[
            {
                "id": 1,
                "nome": "Agachamento Gamificado",
                "nivel_dificuldade": "Médio",
            }
        ]
    )
    repo_prescricoes = FakeRepositorioPrescricoes()

    dados = {
        "paciente_id": "CPF-JOAO-SOUZA",
        "exercicio_id": 1,
        "series": 3,
        "repeticoes": 10,
        "duracao_minutos": 15,
        "frequencia_semanal": 5,
        "nivel_dificuldade": "Médio",
    }

    erros, mensagem = prescrever_exercicio(dados, repo_exercicios, repo_prescricoes)

    assert erros == []
    assert mensagem == "Exercício prescrito com sucesso"
    assert repo_prescricoes.salvou is True

    # Conferindo se foi salva vinculada ao paciente
    lista = repo_prescricoes.listar_por_paciente("CPF-JOAO-SOUZA")
    assert len(lista) == 1
    presc = lista[0]
    assert presc["nome_exercicio"] == "Agachamento Gamificado"
    assert presc["series"] == 3
    assert presc["repeticoes"] == 10
    assert presc["duracao_minutos"] == 15
    assert presc["frequencia_semanal"] == 5


def test_tentativa_prescricao_sem_parametros_obrigatorios():
    """
    Cenário do doc:
    - Deixa "repetições" em branco
    - Deve exibir: "Parâmetros obrigatórios do exercício devem ser preenchidos"
    """
    repo_exercicios = FakeRepositorioExercicios(
        exercicios=[
            {"id": 1, "nome": "Agachamento Gamificado", "nivel_dificuldade": "Médio"}
        ]
    )
    repo_prescricoes = FakeRepositorioPrescricoes()

    dados = {
        "paciente_id": "CPF-JOAO-SOUZA",
        "exercicio_id": 1,
        "series": 3,
        "repeticoes": None,  # em branco / inválido
        "duracao_minutos": 15,
        "frequencia_semanal": 5,
    }

    erros, mensagem = prescrever_exercicio(dados, repo_exercicios, repo_prescricoes)

    assert "Parâmetros obrigatórios do exercício devem ser preenchidos" in erros
    assert mensagem is None
    assert repo_prescricoes.salvou is False


def test_biblioteca_de_exercicios_vazia():
    """
    Cenário do doc:
    - Não existem exercícios cadastrados
    - Mensagem: "Não há exercícios disponíveis para prescrição"
    """
    repo_exercicios = FakeRepositorioExercicios(exercicios=[])
    repo_prescricoes = FakeRepositorioPrescricoes()

    dados = {
        "paciente_id": "CPF-JOAO-SOUZA",
        "exercicio_id": 1,
        "series": 3,
        "repeticoes": 10,
        "duracao_minutos": 15,
        "frequencia_semanal": 5,
    }

    erros, mensagem = prescrever_exercicio(dados, repo_exercicios, repo_prescricoes)

    assert "Não há exercícios disponíveis para prescrição" in erros
    assert mensagem is None
    assert repo_prescricoes.salvou is False


def test_exercicio_nao_encontrado_na_biblioteca():
    """
    Caso extra (não explícito no Gerkin, mas importante):
    - Biblioteca não está vazia, mas ID não existe
    - Mensagem: "Exercício gamificado não encontrado na biblioteca"
    """
    repo_exercicios = FakeRepositorioExercicios(
        exercicios=[
            {"id": 2, "nome": "Outro Exercício", "nivel_dificuldade": "Fácil"}
        ]
    )
    repo_prescricoes = FakeRepositorioPrescricoes()

    dados = {
        "paciente_id": "CPF-JOAO-SOUZA",
        "exercicio_id": 999,  # inexistente
        "series": 3,
        "repeticoes": 10,
        "duracao_minutos": 15,
        "frequencia_semanal": 5,
    }

    erros, mensagem = prescrever_exercicio(dados, repo_exercicios, repo_prescricoes)

    assert "Exercício gamificado não encontrado na biblioteca" in erros
    # ainda assim, se faltar algum obrigatório/for inválido, pode ter tb "Parâmetros..."
    assert mensagem is None
    assert repo_prescricoes.salvou is False