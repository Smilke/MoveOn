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

class RepositorioNotificacaoMemoria:
    def __init__(self):
        self._notificacoes = []
        self._proximo_id = 1

    def salvar(self, notificacao: dict):
        noti_com_id = notificacao.copy()
        noti_com_id["id"] = self._proximo_id
        self._proximo_id += 1

        self._notificacoes.append(noti_com_id)
        return noti_com_id

    def listar_por_paciente(self, paciente_id: str):
        return [
            n for n in self._notificacoes
            if n.get("paciente_id") == paciente_id
        ]

