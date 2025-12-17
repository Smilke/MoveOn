import sys
from pathlib import Path

# permite importar arquivos da pasta backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from cadastrar_paciente import cadastrar_paciente

class FakeRepositorioPaciente:
    def __init__(self, existentes=None):
        # existentes vai ser uma lista de tuplas (cpf, fisioterapeuta_id)
        self.pacientes_existentes = set(existentes or [])
        self.salvou = False
        self.ultimo_salvo = None

    def existe_paciente(self, cpf, fisioterapeuta_id):
        return (cpf, fisioterapeuta_id) in self.pacientes_existentes

    def salvar(self, dados):
        self.salvou = True
        self.ultimo_salvo = dados
        # também adiciona na lista de existentes
        chave = (dados["cpf"], dados["fisioterapeuta_id"])
        self.pacientes_existentes.add(chave)


def test_deve_salvar_paciente_quando_dados_validos_e_sem_duplicidade():
    repo = FakeRepositorioPaciente()
    fisioterapeuta_id = "FISIO123"

    dados = {
        "nome": "Maria da Silva",
        "cpf": "12345678901",
        "idade": 30,
        "situacao": "em tratamento",
    }

    erros = cadastrar_paciente(dados, fisioterapeuta_id, repo)

    assert erros == []
    assert repo.salvou is True
    assert repo.ultimo_salvo is not None
    assert repo.ultimo_salvo["fisioterapeuta_id"] == fisioterapeuta_id


def test_nao_deve_salvar_quando_validacao_falhar():
    repo = FakeRepositorioPaciente()
    fisioterapeuta_id = "FISIO123"

    dados = {
        "nome": "",                 # inválido de propósito
        "cpf": "1234",              # inválido
        "idade": 0,                 # inválido
        "situacao": "em tratamento",
    }

    erros = cadastrar_paciente(dados, fisioterapeuta_id, repo)

    # tem que vir pelo menos um erro de validação
    assert len(erros) > 0
    # e não pode tentar salvar
    assert repo.salvou is False


def test_nao_deve_permitir_paciente_com_mesmo_cpf_para_mesmo_fisioterapeuta():
    fisioterapeuta_id = "FISIO123"
    cpf_duplicado = "12345678901"

    # já existe paciente com esse cpf pra esse fisio
    repo = FakeRepositorioPaciente(
        existentes=[(cpf_duplicado, fisioterapeuta_id)]
    )

    dados = {
        "nome": "Outro Paciente",
        "cpf": cpf_duplicado,
        "idade": 40,
        "situacao": "em tratamento",
    }

    erros = cadastrar_paciente(dados, fisioterapeuta_id, repo)

    assert "Paciente com esse CPF já cadastrado para este fisioterapeuta." in erros
    assert repo.salvou is False
