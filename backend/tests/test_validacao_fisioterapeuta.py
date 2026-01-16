import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validacao_de_dados import validar_dados_fisioterapeuta

def test_cadastro_fisioterapeuta_dados_validos_sao_aceitos():
    dados = {
        "nome": "Ana Silva",
        "cpf": "12345678901",
        "cnpj": "",
        "registro": "CREFITO 12345-F",
        "email": "ana@clinica.com",
    }   

    erros = validar_dados_fisioterapeuta(dados)

    assert erros == []

def test_cadastro_fisioterapeuta_nome_obrigatorio():
    dados = {
        "nome": "",
        "cpf": "12345678901",
        "cnpj": "",
        "registro": "CREFITO 12345-F",
        "email": "ana@clinica.com",
    }
    erros = validar_dados_fisioterapeuta(dados)

    assert "Nome é obrigatório." in erros

def test_cadastro_fisioterapeuta_cpf_invalido():
    dados = {
        "nome": "Ana Silva",
        "cpf": "1234",

        "cnpj": "",
        "registro": "CREFITO 12345-F",
        "email": "ana@clinica.com",
    }

    erros = validar_dados_fisioterapeuta(dados)

    assert "CPF inválido" in erros

    
def teste_cadastro_fisioterapeuta_email_obrigatorio():
    dados = {
        "nome": "Ana Silva",
        "cpf": "12345678901",
        "cnpj": "",
        "registro": "CREFITO 12345-F",
        "email": "anaclinica.com",
    }
    erros = validar_dados_fisioterapeuta(dados)

    assert "Email inválido." in erros      

def test_cadastro_fisioterapeuta_email_obrigatorio():
    dados = {
        "nome": "Ana Silva",
        "cpf": "12345678901",
        "cnpj": "",
        "registro": "CREFITO 12345-F",
        "email": "",
    }
    erros = validar_dados_fisioterapeuta(dados)

    assert "Email é obrigatório." in erros

def test_cadastro_fisioterapeuta_registro_obrigatorio():
    dados = {
        "nome": "Ana Silva",
        "cpf": "12345678901",
        "cnpj": "",
        "registro": "",
        "email": "ana@clinica.com",
    }

    erros = validar_dados_fisioterapeuta(dados)

    assert "Registro é obrigatório." in erros
    
def test_cadastro_fisioterapeuta_registro_invalido():
    dados = {
        "nome": "Ana Silva",
        "cpf": "12345678901",
        "cnpj": "",
        "registro": "12345",
        "email": "ana@clinica.com",
    }

    erros = validar_dados_fisioterapeuta(dados)

    assert "Registro inválido." in erros


