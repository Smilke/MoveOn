from validacao_meta import validar_meta_paciente


def cadastrar_meta(dados, repositorio):
    erros = validar_meta_paciente(dados)

    if erros:
        return erros

    meta_para_salvar = dados.copy()
    meta_para_salvar["status"] = "ativa"

    repositorio.salvar(meta_para_salvar)

    return []


def atualizar_status_meta(meta_id, novo_status, repositorio):
    """
    Atualiza o status de uma meta.

    Status permitidos:
    - 'ativa'
    - 'em_andamento'
    - 'concluida'
    - 'nao_atingida'
    """
    status_validos = {"ativa", "em_andamento", "concluida", "nao_atingida"}

    if novo_status not in status_validos:
        return ["Status inválido."]

    meta = repositorio.obter_por_id(meta_id)
    if meta is None:
        return ["Meta não encontrada."]

    meta["status"] = novo_status

    return []
