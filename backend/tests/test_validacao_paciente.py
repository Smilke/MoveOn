import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from validacao_paciente import validar_dados_paciente

def test_validacao_paciente_dados_validos_sao_aceitos():
    dados = {
        "nome": "João Silva",
        "idade": 30,
        "cpf": "12345678900",
        "situacao" : "em tratamento",


    } 

    erros = validar_dados_paciente(dados)
    assert erros == []

def test_validacao_paciente_nome_obrigatorio():
    dados = {
        "nome" : "",
        "idade": 30,
        "cpf": "12345678900",
        "situacao" : "em tratamento",
    }

    erros = validar_dados_paciente(dados)
    assert "Nome é obrigatório" in erros

def test_validacao_cpf_invalido():
    dados = {
        "nome": "Maria Souza",
        "idade": 25,
        "cpf": "12345",
        "situacao" : "em tratamento",
    }

    erros = validar_dados_paciente(dados)
    assert "CPF inválido" in erros

def test_validacao_idade_deve_ser_maior_que_zero():
    dados = {
        "nome": "Carlos Pereira",
        "idade": 0,
        "cpf": "98765432100",
        "situacao" : "em tratamento",
    }

    erros = validar_dados_paciente(dados)
    assert "Idade deve ser maior que zero" in erros

def test_validacao_paciente_idade_deve_ser_numerica ():

    dados = {
        "nome": "Ana Lima",
        "idade": "abc",
        "cpf": "12345678900",
        "situacao" : "em tratamento",
    }

    erros = validar_dados_paciente(dados)
    assert "Idade deve ser numérica" in erros


