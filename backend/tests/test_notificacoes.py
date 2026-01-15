from datetime import datetime
from repositorio_memoria import RepositorioNotificacaoMemoria
from notificacoes import (
    registrar_notificacao,
    listar_notificacoes_paciente,
)


def test_registrar_notificacao_cria_registro_com_campos_basicos():
    repo = RepositorioNotificacaoMemoria()

    paciente_id = "12345678901"
    tipo = "novo_exercicio"
    mensagem = "Seu fisioterapeuta prescreveu um novo exercício."

    registrar_notificacao(repo, paciente_id, tipo, mensagem)

    assert len(repo._notificacoes) == 1  # por enquanto, acessando direto
    noti = repo._notificacoes[0]

    assert noti["paciente_id"] == paciente_id
    assert noti["tipo"] == tipo
    assert noti["mensagem"] == mensagem
    assert isinstance(noti["data_hora"], datetime)
    assert noti["lida"] is False


def test_listar_notificacoes_de_paciente_sem_notificacoes_retorna_lista_vazia():
    repo = RepositorioNotificacaoMemoria()

    resultado = listar_notificacoes_paciente(repo, "99999999999")

    assert resultado == []


def test_listar_notificacoes_retorna_em_ordem_da_mais_recente_para_a_mais_antiga():
    repo = RepositorioNotificacaoMemoria()
    paciente_id = "12345678901"

    registrar_notificacao(repo, paciente_id, "novo_exercicio", "Msg 1")
    registrar_notificacao(repo, paciente_id, "meta_atualizada", "Msg 2")
    registrar_notificacao(repo, paciente_id, "feedback", "Msg 3")

    notificacoes = listar_notificacoes_paciente(repo, paciente_id)

    assert len(notificacoes) == 3
    assert notificacoes[0]["mensagem"] == "Msg 3"
    assert notificacoes[1]["mensagem"] == "Msg 2"
    assert notificacoes[2]["mensagem"] == "Msg 1"
