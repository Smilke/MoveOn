import email
from validacao_de_dados import validar_dados_fisioterapeuta

def cadastrar_fisioterapeuta(dados, repositorio):
    erros = validar_dados_fisioterapeuta(dados)

    if erros:
        return erros
    

    cpf = dados.get("cpf", "").strip()
    email = dados.get("email", "").strip()

    if repositorio.existe_cpf(cpf):
        return ["CPF já cadastrado."]
    
    if repositorio.existe_email(email):
        return ["Email já cadastrado."]
    
    repositorio.salvar(dados)
    return []
