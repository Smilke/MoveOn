from validacao_paciente import validar_dados_paciente

def cadastrar_paciente(dados, fisioterapeuta_id, repositorio):
    erros = validar_dados_paciente(dados)
    if erros:
        return erros
    
    # Verifica duplicidade de CPF para o mesmo fisioterapeuta
    cpf = str(dados.get("cpf", "")).strip()

    if repositorio.existe_paciente(cpf, fisioterapeuta_id):
        return ["Paciente com esse CPF já cadastrado para este fisioterapeuta."]

    dados_para_salvar = dict(dados)
    dados_para_salvar["fisioterapeuta_id"] = fisioterapeuta_id
    

    repositorio.salvar(dados_para_salvar)
    return []    