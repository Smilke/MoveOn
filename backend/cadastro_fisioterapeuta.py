import hashlib
from validacao_de_dados import validar_dados_fisioterapeuta


def hash_senha(senha: str) -> str:
    """
    Gera um hash SHA-256 da senha.
    Simples, só pra não guardar senha em texto puro.
    """
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def cadastrar_fisioterapeuta(dados, repositorio):
    """
    - Valida os dados (nome, cpf, email, registro, etc.)
    - Verifica duplicidade de CPF e e-mail
    - Se tiver campo 'senha' em dados, gera 'senha_hash'
      e remove a senha crua antes de salvar.
    """
    erros = validar_dados_fisioterapeuta(dados)
    if erros:
        return erros

    cpf = dados.get("cpf", "").strip()
    email = dados.get("email", "").strip()

    if repositorio.existe_cpf(cpf):
        return ["CPF já cadastrado."]

    if repositorio.existe_email(email):
        return ["Email já cadastrado."]

    # Monta o dicionário final a ser salvo
    dados_para_salvar = dict(dados)

    senha = dados_para_salvar.get("senha")
    if senha:
        dados_para_salvar["senha_hash"] = hash_senha(senha)
        # não guardamos a senha em texto puro
        dados_para_salvar.pop("senha", None)

    repositorio.salvar(dados_para_salvar)
    return []
