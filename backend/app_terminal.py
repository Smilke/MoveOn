from cadastro_fisioterapeuta import cadastrar_fisioterapeuta
from cadastrar_paciente import cadastrar_paciente


# --- Repositórios em memória (só existem enquanto o programa roda) ---


class RepositorioFisioMemoria:
    def __init__(self):
        self._fisioterapeutas = []

    def existe_cpf(self, cpf: str) -> bool:
        return any(f["cpf"] == cpf for f in self._fisioterapeutas)

    def existe_email(self, email: str) -> bool:
        return any(f["email"] == email for f in self._fisioterapeutas)

    def salvar(self, dados: dict) -> None:
        self._fisioterapeutas.append(dados)

    def listar(self) -> list[dict]:
        return list(self._fisioterapeutas)


class RepositorioPacienteMemoria:
    def __init__(self):
        self._pacientes = []

    def existe_paciente(self, cpf: str, fisioterapeuta_id: str) -> bool:
        return any(
            p["cpf"] == cpf and p["fisioterapeuta_id"] == fisioterapeuta_id
            for p in self._pacientes
        )

    def salvar(self, dados: dict) -> None:
        self._pacientes.append(dados)

    def listar(self) -> list[dict]:
        return list(self._pacientes)


# --- Fluxos de terminal ---


def cadastrar_fisio_terminal(repo_fisio: RepositorioFisioMemoria) -> None:
    print("\n=== Cadastro de Fisioterapeuta ===")
    nome = input("Nome: ").strip()
    cpf = input("CPF (apenas números): ").strip()
    registro = input("Registro profissional (ex: CREFITO 12345-F): ").strip()
    email = input("Email: ").strip()
    cnpj = input("CNPJ (opcional): ").strip()

    dados = {
        "nome": nome,
        "cpf": cpf,
        "registro": registro,
        "email": email,
        "cnpj": cnpj,
    }

    erros = cadastrar_fisioterapeuta(dados, repo_fisio)

    if erros:
        print("\n⚠ Erros ao cadastrar fisioterapeuta:")
        for e in erros:
            print(f" - {e}")
    else:
        print("\n✅ Fisioterapeuta cadastrado com sucesso!")


def listar_fisios_terminal(repo_fisio: RepositorioFisioMemoria) -> None:
    print("\n=== Fisioterapeutas cadastrados ===")
    fisios = repo_fisio.listar()

    if not fisios:
        print("Nenhum fisioterapeuta cadastrado ainda.")
        return

    for f in fisios:
        print(
            f"- {f['nome']} | CPF: {f['cpf']} | Registro: {f['registro']} | Email: {f['email']}"
        )


def cadastrar_paciente_terminal(
    repo_paciente: RepositorioPacienteMemoria,
    repo_fisio: RepositorioFisioMemoria,
) -> None:
    print("\n=== Cadastro de Paciente ===")
    cpf_fisio = input("CPF do fisioterapeuta responsável: ").strip()


    if not repo_fisio.existe_cpf(cpf_fisio):
        print("\n⚠ Fisioterapeuta não encontrado. Cadastre o fisioterapeuta primeiro.")
        return

    nome = input("Nome do paciente: ").strip()
    cpf_paciente = input("CPF do paciente (apenas números): ").strip()
    idade = input("Idade do paciente: ").strip()
    situacao = input("Situação (ex: em tratamento, alta): ").strip() or "em tratamento"

    dados_paciente = {
        "nome": nome,
        "cpf": cpf_paciente,
        "idade": idade,
        "situacao": situacao,
    }


    erros = cadastrar_paciente(dados_paciente, cpf_fisio, repo_paciente)

    if erros:
        print("\n⚠ Erros ao cadastrar paciente:")
        for e in erros:
            print(f" - {e}")
    else:
        print("\n✅ Paciente cadastrado com sucesso!")


def listar_pacientes_terminal(repo_paciente: RepositorioPacienteMemoria) -> None:
    print("\n=== Pacientes cadastrados ===")
    pacientes = repo_paciente.listar()

    if not pacientes:
        print("Nenhum paciente cadastrado ainda.")
        return

    for p in pacientes:
        print(
            f"- {p['nome']} | CPF: {p['cpf']} | Idade: {p['idade']} | "
            f"Situação: {p['situacao']} | Fisioterapeuta: {p['fisioterapeuta_id']}"
        )


def main() -> None:
    repo_fisio = RepositorioFisioMemoria()
    repo_paciente = RepositorioPacienteMemoria()

    while True:
        print("\n=== Menu MoveOn (terminal) ===")
        print("1 - Cadastrar fisioterapeuta")
        print("2 - Listar fisioterapeutas")
        print("3 - Cadastrar paciente vinculado a fisioterapeuta")
        print("4 - Listar pacientes")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            print("\nSaindo...")
            break
        elif opcao == "1":
            cadastrar_fisio_terminal(repo_fisio)
        elif opcao == "2":
            listar_fisios_terminal(repo_fisio)
        elif opcao == "3":
            cadastrar_paciente_terminal(repo_paciente, repo_fisio)
        elif opcao == "4":
            listar_pacientes_terminal(repo_paciente)
        else:
            print("\nOpção inválida, tente novamente.")


if __name__ == "__main__":
    main()