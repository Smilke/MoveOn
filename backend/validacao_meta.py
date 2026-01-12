def validar_meta_paciente(dados):
    erros = []

    # Campos principais
    paciente_id = str(dados.get("paciente_id", "")).strip()
    fisio_id = str(dados.get("fisioterapeuta_id", "")).strip()
    descricao = str(dados.get("descricao", "")).strip()
    data_inicio = str(dados.get("data_inicio", "")).strip()
    data_fim = str(dados.get("data_fim", "")).strip()

    if not paciente_id:
        erros.append("ID do paciente é obrigatório.")

    if not fisio_id:
        erros.append("ID do fisioterapeuta é obrigatório.")

    if not descricao:
        erros.append("Descrição da meta é obrigatória.")

    if not data_inicio or not data_fim:
        erros.append("Período de validade (início e fim) é obrigatório.")



    return erros
