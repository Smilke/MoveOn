from datetime import datetime

from validacao_feedback import validar_feedback_paciente

def cadastrar_feedback(dados, repositorio):

    erros = validar_feedback_paciente(dados)
    if erros:
        return erros
    


    dados_para_salvar = dados.copy()
    dados_para_salvar["data_hora"] = datetime.now().isoformat()
    repositorio.salvar(dados_para_salvar)

    return []
