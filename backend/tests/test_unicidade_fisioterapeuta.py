import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cadastro_fisioterapeuta import cadastrar_fisioterapeuta, hash_senha


class FakeRepositorioFisio:
    def __init__(self, existentes=None):
        # existentes: cpfs ou emails
        self.cpfs_existentes = set(existentes or [])
        self.emails_existentes = set(existentes or [])
        self.salvou = False
        self.ultimo_salvo = None

    def existe_cpf(self, cpf):
        return cpf in self.cpfs_existentes

    def existe_email(self, email):
        return email in self.emails_existentes

    def salvar(self, dados):
        self.salvou = True
        self.ultimo_salvo = dados


def test_deve_recusar_quando_cpf_ja_existente():
    cpf_duplicado = "52998224725"
    repo = FakeRepositorioFisio(existentes=[cpf_duplicado])

    dados = {
        "nome": "João Pereira",
        "cpf": cpf_duplicado,
        "registro": "CREFITO 12345-F",
        "email": "ana@exemplo.com",
        "senha": "Senha123",
    }

    erros = cadastrar_fisioterapeuta(dados, repo)

    assert "CPF já cadastrado." in erros
    assert repo.salvou is False


def test_deve_recusar_quando_email_ja_existente():
    email_duplicado = "ana@exemplo.com"
    repo = FakeRepositorioFisio(existentes=[email_duplicado])

    dados = {
        "nome": "Ana Silva",
        "cpf": "12345678901",
        "registro": "CREFITO 54321-F",
        "email": email_duplicado,
        "senha": "Senha123",
    }

    erros = cadastrar_fisioterapeuta(dados, repo)

    assert "Email já cadastrado." in erros
    assert repo.salvou is False


def test_deve_salvar_quando_dados_validos_e_sem_duplicidades():
    repo = FakeRepositorioFisio()

    dados = {
        "nome": "Ana Fisioterapeuta",
        "cpf": "98765432100",
        "registro": "CREFITO 67890-F",
        "email": "ana@clinica.com",
        "cnpj": "",
        "senha": "SenhaSuperSegura123",
    }

    erros = cadastrar_fisioterapeuta(dados, repo)

    assert erros == []
    assert repo.salvou is True
    assert repo.ultimo_salvo is not None

    # Verificação de segurança da senha
    assert "senha" not in repo.ultimo_salvo

    # Verificação do hash da senha
    assert "senha_hash" in repo.ultimo_salvo
    assert repo.ultimo_salvo["senha_hash"] == hash_senha("SenhaSuperSegura123")


def test_nao_deve_salvar_quando_validacao_falhar():
    repo = FakeRepositorioFisio()  # repositório vazio

    dados = {
        "nome": "",                  # inválido de propósito
        "cpf": "1234",               # também inválido
        "registro": "CREFITO 12345-F",
        "email": "ana@clinica.com",
        "cnpj": "",
        "senha": "AlgumaSenha",
    }

    erros = cadastrar_fisioterapeuta(dados, repo)

    assert len(erros) > 0
    assert repo.salvou is False
