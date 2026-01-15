def validar_feedback_paciente(dados: dict) -> list[str]:
    """
    Valida os dados de feedback enviados pelo paciente.

    Espera um dicionário com (idealmente):
      - paciente_id: str
      - fisioterapeuta_id: str
      - mensagem ou feedback: str
      - avaliacao: int (1 a 5, opcional)

    Retorna uma lista de strings com mensagens de erro.
    Se a lista vier vazia, significa que está tudo ok.
    """
    erros: list[str] = []

    # --- Paciente ---
    paciente_id = str(dados.get("paciente_id", "")).strip()
    if not paciente_id:
        erros.append("Paciente é obrigatório.")

    # --- Fisioterapeuta ---
    fisioterapeuta_id = str(dados.get("fisioterapeuta_id", "")).strip()
    if not fisioterapeuta_id:
        erros.append("Fisioterapeuta é obrigatório.")

    # --- Mensagem / feedback ---
    # aceita tanto "mensagem" quanto "feedback" como chave
    mensagem = (
        (dados.get("mensagem") or dados.get("feedback") or "")
        .strip()
    )
    if not mensagem:
        erros.append("Mensagem é obrigatória.")

    # --- Avaliação (opcional, mas se vier tem que ser 1 a 5) ---
    avaliacao = dados.get("avaliacao", None)
    if avaliacao is not None:
        try:
            avaliacao_int = int(avaliacao)
        except (TypeError, ValueError):
            erros.append("Avaliação deve ser um número inteiro entre 1 e 5.")
        else:
            if avaliacao_int < 1 or avaliacao_int > 5:
                erros.append("Avaliação deve ser um número inteiro entre 1 e 5.")

    return erros
