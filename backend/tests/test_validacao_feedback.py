import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from validacao_feedback import validar_feedback_paciente

def test_feedback_valido_e_aceito():
    dados = {
        "paciente_id" : "12345678901",
        "fisioterapeuta_id" : "11122233344",
        "feedback" : "O atendimento foi excelente e muito profissional.",
        "avaliacao" : 4

    }

    erros = validar_feedback_paciente(dados)
    assert erros == []

def test_feedback_valido_sem_avaliacao_tambem_e_aceito():
    dados = {
        "paciente_id" : "12345678901",
        "fisioterapeuta_id" : "11122233344",
        "feedback" : "O atendimento foi bom, mas poderia melhorar em alguns aspectos.",
    }

    erros = validar_feedback_paciente(dados)
    assert erros == []

def test_feedback_deve_ter_paciente_id_obrigatorio():
    dados = {
        "paciente_id" : "",
        "fisioterapeuta_id" : "11122233344",
        "feedback" : "O atendimento foi excelente e muito profissional.",
        "avaliacao" : 5
    }

    erros = validar_feedback_paciente(dados)
    assert "ID do paciente é obrigatório." in erros

def test_feedback_deve_ter_fisioterapeuta_id_obrigatorio():
    dados = {
        "paciente_id" : "12345678901",
        "fisioterapeuta_id" : "",
        "feedback" : "O atendimento foi excelente e muito profissional.",
        "avaliacao" : 5
    }

    erros = validar_feedback_paciente(dados)
    assert "ID do fisioterapeuta é obrigatório." in erros

def test_feedback_deve_ter_mensagem_obrigatoria():
    dados = {
        "paciente_id" : "12345678901",
        "fisioterapeuta_id" : "11122233344",
        "feedback" : "",
        "avaliacao" : 5
    }

    erros = validar_feedback_paciente(dados)
    assert "Mensagem é obrigatória." in erros

def test_feedback_com_avaliacao_invalida_menor_que_1():
    dados = {
        "paciente_id" : "12345678901",
        "fisioterapeuta_id" : "11122233344",
        "feedback" : "O atendimento foi excelente e muito profissional.",
        "avaliacao" : 0
    }

    erros = validar_feedback_paciente(dados)
    assert "Avaliação deve ser um número entre 1 e 5." in erros

def test_feedback_com_avaliacao_invalida_maior_que_5():
    dados = {
        "paciente_id" : "12345678901",
        "fisioterapeuta_id" : "11122233344",
        "feedback" : "O atendimento foi excelente e muito profissional.",
        "avaliacao" : 6
    }

    erros = validar_feedback_paciente(dados)
    assert "Avaliação deve ser um número entre 1 e 5." in erros


