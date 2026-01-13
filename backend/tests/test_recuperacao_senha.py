import sys
from pathlib import Path

# permite importar arquivos da pasta backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from recuperacao_senha import (
    solicitar_recuperacao_senha,
    redefinir_senha,
)


class FakeRepoFisio:
    def __init__(self, fisios=None):
        self._fisioterapeutas = fisios or []


class FakeRepoPaciente:
    def __init__(self, pacientes=None):
        self._pacientes = pacientes or []


class FakeRepoTokens:
    def __init__(self):
        self._tokens = {}
        self._proximo = 1

    def criar_token(self, tipo, email):
        token = f"token-{self._proximo}"
        self._proximo += 1
        self._tokens[token] = {"tipo": tipo, "email": email}
        return token

    def obter_dados(self, token):
        return self._tokens.get(token)

    def invalidar(self, token):
        self._tokens.pop(token, None)


def test_solicitacao_recuperacao_cria_token_para_email_de_fisio():
    repo_fisio = FakeRepoFisio(
        fisios=[
            {
                "nome": "Ana Fisio",
                "email": "ana@exemplo.com",
                "senha_hash": "hash_antigo",
            }
        ]
    )
    repo_paciente = FakeRepoPaciente()
    repo_tokens = FakeRepoTokens()

    erros, token = solicitar_recuperacao_senha(
        "ana@exemplo.com",
        repo_fisio,
        repo_paciente,
        repo_tokens,
    )

    assert erros == []
    assert token is not None
    dados_token = repo_tokens.obter_dados(token)
    assert dados_token["tipo"] == "fisioterapeuta"
    assert dados_token["email"] == "ana@exemplo.com"


def test_solicitacao_recuperacao_retorna_erro_quando_email_nao_existe():
    repo_fisio = FakeRepoFisio()
    repo_paciente = FakeRepoPaciente()
    repo_tokens = FakeRepoTokens()

    erros, token = solicitar_recuperacao_senha(
        "naoexiste@exemplo.com",
        repo_fisio,
        repo_paciente,
        repo_tokens,
    )

    assert "E-mail não encontrado." in erros
    assert token is None


def test_redefinir_senha_atualiza_hash_e_invalida_token():
    from cadastrar_paciente import hash_senha as hash_paciente

    email = "paciente@exemplo.com"
    senha_antiga = "SenhaAntiga123"
    senha_nova = "SenhaNova456"

    repo_fisio = FakeRepoFisio()
    repo_paciente = FakeRepoPaciente(
        pacientes=[
            {
                "nome": "Paciente",
                "email": email,
                "senha_hash": hash_paciente(senha_antiga),
            }
        ]
    )
    repo_tokens = FakeRepoTokens()
    token = repo_tokens.criar_token("paciente", email)

    erros = redefinir_senha(
        token,
        senha_nova,
        repo_fisio,
        repo_paciente,
        repo_tokens,
    )

    assert erros == []

    # token deve ter sido invalidado
    assert repo_tokens.obter_dados(token) is None

    # senha_hash deve ter sido atualizada
    paciente = repo_paciente._pacientes[0]
    assert paciente["senha_hash"] == hash_paciente(senha_nova)
