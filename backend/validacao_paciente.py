import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def validar_dados_paciente(dados):
    erros = []

    # --- validação do nome ---
    nome = dados.get("nome", "").strip()
    if not nome:
        erros.append("Nome é obrigatório")

    # --- validação do CPF ---
    cpf = dados.get("cpf", "").strip()
    # aqui estou usando a mesma lógica simples: 11 dígitos numéricos
    if len(cpf) != 11 or not cpf.isdigit():
        erros.append("CPF inválido")

    # --- validação da idade ---
    idade = dados.get("idade", None)

    if idade is None or idade == "":
        erros.append("Idade é obrigatória")
    else:
        try:
            idade_int = int(idade)
            if idade_int <= 0:
                erros.append("Idade deve ser maior que zero")
        except ValueError:
            erros.append("Idade deve ser numérica")

    return erros

