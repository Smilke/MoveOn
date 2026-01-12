from datetime import datetime


def registrar_notificacao(repo, paciente_id: str, tipo: str, mensagem: str):
    """
    Registra uma notificação simples para o paciente.
    """
    notificacao = {
        "paciente_id": paciente_id,
        "tipo": tipo,
        "mensagem": mensagem,
        "data_hora": datetime.now(),
        "lida": False,
    }

    return repo.salvar(notificacao)


def listar_notificacoes_paciente(repo, paciente_id: str):
    """
    Lista notificações de um paciente em ordem da mais recente para a mais antiga.
    """
    notificacoes = repo.listar_por_paciente(paciente_id)

    # ordena por data_hora desc (mais nova primeiro)
    notificacoes_ordenadas = sorted(
        notificacoes,
        key=lambda n: n["data_hora"],
        reverse=True,
    )

    return notificacoes_ordenadas
