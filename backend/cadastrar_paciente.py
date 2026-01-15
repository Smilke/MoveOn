import hashlib
from validacao_paciente import validar_dados_paciente


def hash_senha(senha: str) -> str:
    """Gera um hash SHA-256 da senha (mesma lógica usada no login)."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def cadastrar_paciente(dados, fisioterapeuta_id, repositorio):
    """
    Cadastra um paciente vinculado a um fisioterapeuta, garantindo:
    - validação dos dados (nome, cpf, idade, etc.)
    - não permitir paciente com mesmo CPF para o mesmo fisio
    - salvar senha como hash (senha_hash), NUNCA em texto puro
    """
    # 1) Valida dados básicos do paciente (nome, cpf, idade, etc.)
    erros = validar_dados_paciente(dados)
    if erros:
        return erros
    
    # 2) Verifica duplicidade de CPF para o mesmo fisioterapeuta
    cpf = str(dados.get("cpf", "")).strip()

    if repositorio.existe_paciente(cpf, fisioterapeuta_id):
        return ["Paciente com esse CPF já cadastrado para este fisioterapeuta."]

    # 3) Prepara o dicionário que realmente será salvo
    dados_para_salvar = dict(dados)
    dados_para_salvar["fisioterapeuta_id"] = fisioterapeuta_id

    # 4) Se tiver senha, gera o hash e remove a senha em texto puro
    senha = dados_para_salvar.get("senha")
    if senha:
        dados_para_salvar["senha_hash"] = hash_senha(senha)
        dados_para_salvar.pop("senha", None)

    # 5) Salva no repositório
    repositorio.salvar(dados_para_salvar)
    return []
