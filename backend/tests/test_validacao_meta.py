import sys
from pathlib import Path

# Deixa o Python enxergar a pasta backend/
sys.path.insert(0, str(Path(__file__).parent.parent))

from validacao_meta import validar_meta_paciente


def test_meta_valida_e_aceita():
    dados = {
        "paciente_id": "12345678901",
        "fisioterapeuta_id": "11122233344",
        "descricao": "Reduzir dor média para <= 3 em 4 semanas.",
        "criterio_sucesso": "Paciente relata dor média <= 3 por 7 dias seguidos.",
        "data_inicio": "2025-01-01",
        "data_fim": "2025-01-31",
    }

    erros = validar_meta_paciente(dados)

    assert erros == []


def test_meta_deve_ter_paciente_id_obrigatorio():
    dados = {
        "paciente_id": "",
        "fisioterapeuta_id": "11122233344",
        "descricao": "Realizar exercícios 5x por semana.",
        "criterio_sucesso": "Paciente registra 5 sessões por semana.",
        "data_inicio": "2025-01-01",
        "data_fim": "2025-01-31",
    }

    erros = validar_meta_paciente(dados)

    assert "ID do paciente é obrigatório." in erros


def test_meta_deve_ter_fisioterapeuta_id_obrigatorio():
    dados = {
        "paciente_id": "12345678901",
        "fisioterapeuta_id": "",
        "descricao": "Realizar exercícios 5x por semana.",
        "criterio_sucesso": "Paciente registra 5 sessões por semana.",
        "data_inicio": "2025-01-01",
        "data_fim": "2025-01-31",
    }

    erros = validar_meta_paciente(dados)

    assert "ID do fisioterapeuta é obrigatório." in erros


def test_meta_deve_ter_descricao_obrigatoria():
    dados = {
        "paciente_id": "12345678901",
        "fisioterapeuta_id": "11122233344",
        "descricao": "",
        "criterio_sucesso": "Paciente registra 5 sessões por semana.",
        "data_inicio": "2025-01-01",
        "data_fim": "2025-01-31",
    }

    erros = validar_meta_paciente(dados)

    assert "Descrição da meta é obrigatória." in erros


def test_meta_deve_ter_periodo_de_validade():
    dados = {
        "paciente_id": "12345678901",
        "fisioterapeuta_id": "11122233344",
        "descricao": "Realizar exercícios 5x por semana.",
        "criterio_sucesso": "Paciente registra 5 sessões por semana.",
        "data_inicio": "",
        "data_fim": "",
    }

    erros = validar_meta_paciente(dados)

    assert "Período de validade (início e fim) é obrigatório." in erros
