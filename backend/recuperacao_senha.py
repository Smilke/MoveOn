import uuid

from cadastro_fisioterapeuta import hash_senha as hash_senha_fisio
from cadastrar_paciente import hash_senha as hash_senha_paciente


class RepositorioTokensRecuperacaoMemoria:
    def __init__(self):
        # token -> {"tipo": "fisioterapeuta"|"paciente", "email": "..."}
        self._tokens = {}

    def criar_token(self, tipo: str, email: str) -> str:
        token = uuid.uuid4().hex
        self._tokens[token] = {"tipo": tipo, "email": email}
        return token

    def obter_dados(self, token: str):
        return self._tokens.get(token)

    def invalidar(self, token: str):
        self._tokens.pop(token, None)


# instância global para ser usada nas rotas
repo_tokens_recuperacao = RepositorioTokensRecuperacaoMemoria()


def solicitar_recuperacao_senha(email: str, repo_fisio, repo_paciente, repo_tokens):
    """
    Procura email entre fisioterapeutas e pacientes.
    Se encontrar, cria um token de recuperação e devolve (erros=[], token="...").
    Se não encontrar, devolve (["E-mail não encontrado."], None).
    """
    email = email.strip()

    # 1) tenta achar como fisioterapeuta
    for f in getattr(repo_fisio, "_fisioterapeutas", []):
        if f.get("email") == email:
            token = repo_tokens.criar_token("fisioterapeuta", email)
            return [], token

    # 2) tenta achar como paciente
    for p in getattr(repo_paciente, "_pacientes", []):
        if p.get("email") == email:
            token = repo_tokens.criar_token("paciente", email)
            return [], token

    return ["E-mail não encontrado."], None


def redefinir_senha(token: str, nova_senha: str, repo_fisio, repo_paciente, repo_tokens):
    """
    Dado um token válido e uma nova senha, atualiza o senha_hash
    do usuário correspondente (fisio ou paciente) e invalida o token.
    Retorna [] se deu certo ou lista de erros se deu problema.
    """
    erros = []

    if not nova_senha or len(nova_senha) < 8:
        erros.append("Senha deve ter pelo menos 8 caracteres.")
        return erros

    dados_token = repo_tokens.obter_dados(token)
    if not dados_token:
        erros.append("Token inválido ou expirado.")
        return erros

    tipo = dados_token["tipo"]
    email = dados_token["email"]

    if tipo == "fisioterapeuta":
        lista = getattr(repo_fisio, "_fisioterapeutas", [])
        hash_func = hash_senha_fisio
    else:
        lista = getattr(repo_paciente, "_pacientes", [])
        hash_func = hash_senha_paciente

    for user in lista:
        if user.get("email") == email:
            user["senha_hash"] = hash_func(nova_senha)
            repo_tokens.invalidar(token)
            return []

    erros.append("Usuário associado ao token não foi encontrado.")
    return erros
