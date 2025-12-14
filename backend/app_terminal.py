import repositorio_memoria
from cadastro_fisioterapeuta import cadastrar_fisioterapeuta
from repositorio_memoria import RepositorioFisioMemoria


def main():
    repo = RepositorioFisioMemoria()

    print ("=== Sistema de cadastro de Fisioterapeutas === ")   
    while True:
        print ("Novo cadastro de fisioterapeuta:   ")
        print ("Deixe em branco para sair  ")
        
        nome = input("Nome: ").strip()

        if nome == "":
            print ("Saindo do sistema de cadastro.")
            break
        cpf = input("CPF: ").strip()
        email = input("Email: ").strip()
        registro = input("Registro profissional "
        "(CREFITO no formato CREFITO 12345-F): ").strip()

        cnpj = input("CNPJ da clinica (opcional): ").strip()
        dados = {
            "nome": nome,
            "cpf": cpf,
            "email": email,
            "registro": registro,
            "cnpj": cnpj
        }

        erros = cadastrar_fisioterapeuta(dados, repo)
        

        if erros:
            print ("Erros encontrados no cadastro: ")
            for erro in erros:
                print (" - ", erro)
        else:
            print ("Fisioterapeuta cadastrado com sucesso! ")

if __name__ == "__main__":
    main()


