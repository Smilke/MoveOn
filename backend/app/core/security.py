import hashlib

def hash_senha(senha: str) -> str:
    """
    Gera um hash SHA-256 da senha.
    Simples, só pra não guardar senha em texto puro.
    """
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    """
    Verifica se a senha pura corresponde ao hash.
    """
    return hash_senha(senha_pura) == senha_hash
