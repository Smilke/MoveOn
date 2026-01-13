# backend/cadastro_fisioterapeuta.py

import hashlib
from validacao_de_dados import validar_dados_fisioterapeuta


def hash_senha(senha: str) -> str:
    """Gera um hash SHA-256 da senha (simples, para fins didáticos)."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def cadastrar_fisioterapeuta(dados, repositorio):
    # 1) Validação básica (nome, cpf, registro, email...)
    erros = validar_dados_fisioterapeuta(dados)
    if erros:
        return erros

    cpf = dados.get("cpf", "").strip()
    email = dados.get("email", "").strip()

    # 2) verifica duplicidade
    if repositorio.existe_cpf(cpf):
        return ["CPF já cadastrado."]

    if repositorio.existe_email(email):
        return ["Email já cadastrado."]

    # 3) prepara dados pra salvar
    dados_para_salvar = dict(dados)

    # 4) trata senha -> transforma em hash e remove a crua
    senha = dados_para_salvar.get("senha")
    if senha:
        dados_para_salvar["senha_hash"] = hash_senha(senha)
        dados_para_salvar.pop("senha", None)

    # 5) salva no repositório
    repositorio.salvar(dados_para_salvar)
    return []
