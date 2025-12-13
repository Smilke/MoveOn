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

    # --- validação do email ---
    email = dados.get("email", "")
    if not email or email.strip() == "":
        erros.append("Email é obrigatório.")      
    elif "@" not in email or "." not in email:
        erros.append("Email inválido.")  

    # --- validação do REGISTRO (CREFITO/COFFITO) ---
    registro = dados.get("registro", "")

    if not registro or registro.strip() == "":
        erros.append("Registro é obrigatório.")
    else:
        registro_limpo = registro.strip().upper()

        if not (
            registro_limpo.startswith("CREFITO")
            or registro_limpo.startswith("COFFITO")
        ):
            erros.append("Registro inválido.")

    return erros        
       
