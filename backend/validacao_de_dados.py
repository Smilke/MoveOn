def validar_dados_fisioterapeuta(dados):
    erros = []

    # --- validação do nome ---
    nome = dados.get("nome", "")
    if not nome or nome.strip() == "":
        erros.append("Nome é obrigatório.")

    # --- validação do CPF ---
    cpf = dados.get("cpf", "")

    # regra simples: precisa ter 11 dígitos
    cpf_numeros = "".join(ch for ch in cpf if ch.isdigit())

    if not cpf_numeros:
        erros.append("CPF inválido")
    elif len(cpf_numeros) != 11:
        erros.append("CPF inválido")

    return erros
