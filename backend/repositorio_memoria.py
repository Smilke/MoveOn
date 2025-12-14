class RepositorioFisioMemoria:
    def __init__(self):
        # aqui vamos guardar os fisioterapeutas cadastrados
        self._fisioterapeutas = []

    def existe_cpf(self, cpf: str) -> bool:
        return any(f["cpf"] == cpf for f in self._fisioterapeutas)

    def existe_email(self, email: str):
        return any(f["email"] == email for f in self._fisioterapeutas)

    def salvar(self, dados: dict):
        self._fisioterapeutas.append(dados)

