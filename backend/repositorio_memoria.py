# backend/repositorio_memoria.py

class RepositorioFisioMemoria:
    def __init__(self):
        self._fisioterapeutas = []

    def existe_cpf(self, cpf: str) -> bool:
        return any(f.get("cpf") == cpf for f in self._fisioterapeutas)

    def existe_email(self, email: str) -> bool:
        return any(f.get("email") == email for f in self._fisioterapeutas)

    def salvar(self, dados: dict):
        self._fisioterapeutas.append(dados)

    def listar_todos(self):
        return list(self._fisioterapeutas)


class RepositorioPacienteMemoria:
    def __init__(self):
        self._pacientes = []

    def existe_paciente(self, cpf: str, fisioterapeuta_id: str) -> bool:
        return any(
            p.get("cpf") == cpf and p.get("fisioterapeuta_id") == fisioterapeuta_id
            for p in self._pacientes
        )

    def salvar(self, dados: dict):
        self._pacientes.append(dados)

    def listar_por_fisio(self, fisio_cpf: str):
        return [
            p for p in self._pacientes
            if p.get("fisioterapeuta_id") == fisio_cpf
        ]

    def listar_todos(self):
        return list(self._pacientes)


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

class RepositorioFeedbackMemoria:
    def __init__(self):
        self._feedbacks = []
        self._proximo_id = 1

    def salvar(self, feedback: dict):
        """Salva um feedback em memória e retorna o dict com ID."""
        fb = feedback.copy()
        fb["id"] = self._proximo_id
        self._proximo_id += 1

        self._feedbacks.append(fb)
        return fb

    def listar_por_paciente(self, paciente_id: str):
        """Lista feedbacks de um paciente específico."""
        return [
            f for f in self._feedbacks
            if f.get("paciente_id") == paciente_id
        ]

    def listar_por_fisioterapeuta(self, fisioterapeuta_id: str):
        """Lista feedbacks recebidos por um fisioterapeuta."""
        return [
            f for f in self._feedbacks
            if f.get("fisioterapeuta_id") == fisioterapeuta_id
        ]


# instância global
repo_feedback_memoria = RepositorioFeedbackMemoria()

repo_fisio_memoria = RepositorioFisioMemoria()
repo_paciente_memoria = RepositorioPacienteMemoria()
repo_notificacao_memoria = RepositorioNotificacaoMemoria()
repo_meta_memoria = RepositorioMetaMemoria()
