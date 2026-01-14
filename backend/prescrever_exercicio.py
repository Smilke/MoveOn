# prescrever_exercicio.p

from typing import Any, Dict, List, Optional, Tuple


class ErroPrescricao(Exception):
    """Exceção de domínio (não estamos usando diretamente nos fluxos de API, só por segurança)."""
    pass


def prescrever_exercicio(
    dados: Dict[str, Any],
    repositorio_exercicios,
    repositorio_prescricoes,
) -> Tuple[List[str], Optional[str]]:
    """
    Use case principal da PB03.

    Parâmetros esperados em `dados`:
    - paciente_id (str): identificador do paciente (pode ser CPF ou ID interno).
    - exercicio_id (int): ID do exercício selecionado na biblioteca.
    - series (int): número de séries.
    - repeticoes (int): número de repetições.
    - duracao_minutos (int|None): duração em minutos (opcional).
    - frequencia_semanal (int): vezes por semana.
    - nivel_dificuldade (str|None): opcional, pode sobrescrever o padrão do exercício.

    Retorno:
    - (erros, mensagem_sucesso)
      - Se houver erros: erros != [], mensagem_sucesso = None
      - Se der tudo certo: erros == [], mensagem_sucesso = "Exercício prescrito com sucesso"
    """

    erros: List[str] = []

    # 1) Biblioteca vazia
    # Cenário: "Biblioteca de exercícios vazia"  → msg:
    # "Não há exercícios disponíveis para prescrição"
    if hasattr(repositorio_exercicios, "esta_vazia") and repositorio_exercicios.esta_vazia():
        return ["Não há exercícios disponíveis para prescrição"], None

    # 2) Recuperar exercício escolhido
    exercicio_id = dados.get("exercicio_id")
    exercicio = None

    if exercicio_id is None:
        # vai cair na validação de parâmetros obrigatórios mais abaixo
        exercicio = None
    else:
        exercicio = repositorio_exercicios.obter_por_id(exercicio_id)

    # Se biblioteca não está vazia, mas o ID não existe:
    if exercicio_id is not None and exercicio is None:
        erros.append("Exercício gamificado não encontrado na biblioteca")

    # 3) Validar parâmetros obrigatórios do exercício
    # Critério: se faltar algo essencial, mensagem:
    # "Parâmetros obrigatórios do exercício devem ser preenchidos"
    campos_obrigatorios = ["paciente_id", "exercicio_id", "series", "repeticoes", "frequencia_semanal"]

    parametros_invalidos = False
    for campo in campos_obrigatorios:
        valor = dados.get(campo)

        # vazio, None ou zero para campos numéricos → inválido
        if valor is None or valor == "":
            parametros_invalidos = True
            break

        if isinstance(valor, (int, float)) and valor <= 0:
            parametros_invalidos = True
            break

    if parametros_invalidos:
        erros.append("Parâmetros obrigatórios do exercício devem ser preenchidos")

    # Se já acumulou algum erro, não segue para salvar
    if erros:
        return erros, None

    # 4) Montar objeto de prescrição para salvar no repositório
    paciente_id = str(dados["paciente_id"])

    series = int(dados["series"])
    repeticoes = int(dados["repeticoes"])
    frequencia_semanal = int(dados["frequencia_semanal"])

    # duração é opcional
    duracao_bruta = dados.get("duracao_minutos")
    duracao_minutos = int(duracao_bruta) if duracao_bruta not in (None, "") else None

    # nível de dificuldade pode vir do payload, senão reaproveita do exercício
    nivel_dificuldade = dados.get("nivel_dificuldade") or exercicio.get("nivel_dificuldade")

    # ID gerado pelo repositório
    if hasattr(repositorio_prescricoes, "proximo_id"):
        novo_id = repositorio_prescricoes.proximo_id()
    else:
        # fallback tosco, mas útil em fakes simples
        novo_id = None

    prescricao = {
        "id": novo_id,
        "paciente_id": paciente_id,
        "exercicio_id": exercicio_id,
        "nome_exercicio": exercicio.get("nome"),
        "series": series,
        "repeticoes": repeticoes,
        "duracao_minutos": duracao_minutos,
        "frequencia_semanal": frequencia_semanal,
        "nivel_dificuldade": nivel_dificuldade,
    }

    # 5) Persistir em memória
    repositorio_prescricoes.salvar(prescricao)

    # 6) Mensagem de sucesso alinhada ao documento:
    # "Exercício prescrito com sucesso"
    return [], "Exercício prescrito com sucesso"