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


class RepositorioFeedbackMemoria:
    def __init__(self):
        # aqui vamos guardar os feedbacks cadastrados
        self._feedbacks = []

    def salvar(self, dados: dict):
        self._feedbacks.append(dados)

    def listar_por_paciente(self, paciente_id: str):
        return [
            fb for fb in self._feedbacks if fb.get("paciente_id") == paciente_id
        ]
    
