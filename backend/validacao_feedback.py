def validar_feedback_paciente(dados):
    erros = []

    # pega os campos principais
    paciente_id = str(dados.get("paciente_id", "")).strip()
    fisio_id = str(dados.get("fisioterapeuta_id", "")).strip()

    # aceita tanto "mensagem" quanto "feedback" como campo de texto
    texto = dados.get("mensagem")
    if texto is None:
        texto = dados.get("feedback", "")
    mensagem = str(texto).strip()

    avaliacao = dados.get("avaliacao", None)

    # validações obrigatórias
    if not paciente_id:
        erros.append("ID do paciente é obrigatório.")

    if not fisio_id:
        erros.append("ID do fisioterapeuta é obrigatório.")

    if not mensagem:
        erros.append("Mensagem é obrigatória.")

    if avaliacao is not None:
        try:
            nota = int(avaliacao)
            if nota < 1 or nota > 5:
                erros.append("Avaliação deve ser um número entre 1 e 5.")
        except (TypeError, ValueError):
            erros.append("Avaliação deve ser um número entre 1 e 5.")

    return erros
