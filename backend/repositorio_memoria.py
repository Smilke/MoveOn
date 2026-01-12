class RepositorioFisioMemoria:
    def __init__(self):
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


class RepositorioMetaMemoria:
    def __init__(self):
        self._metas = []
        self._proximo_id = 1

    def salvar(self, meta: dict):
        meta_com_id = meta.copy()
        meta_com_id["id"] = self._proximo_id
        self._proximo_id += 1

        self._metas.append(meta_com_id)
        return meta_com_id

    def listar_por_paciente(self, paciente_id: str):
        return [
            m for m in self._metas
            if m.get("paciente_id") == paciente_id
        ]

    def listar_ativas_por_paciente(self, paciente_id: str):
        return [
            m for m in self._metas
            if m.get("paciente_id") == paciente_id
            and m.get("status") in {"ativa", "em_andamento"}
        ]


    def obter_por_id(self, meta_id: int):
        for m in self._metas:
            if m.get("id") == meta_id:
                return m
        return None
