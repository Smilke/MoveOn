# backend/repositorio_prescricao_memoria.py

"""
Repositórios em memória para PB03 (prescrição de exercícios gamificados).

- RepositorioExercicioMemoria:
    - guarda a "biblioteca" de exercícios
- RepositorioPrescricaoMemoria:
    - guarda as prescrições por paciente
"""

from typing import List, Dict, Any


class RepositorioExercicioMemoria:
    def __init__(self):
        self._exercicios: List[Dict[str, Any]] = []
        self._proximo_id: int = 1

    def esta_vazia(self) -> bool:
        return len(self._exercicios) == 0

    def salvar(self, exercicio: Dict[str, Any]) -> Dict[str, Any]:
        """Adiciona um exercício na biblioteca (só pra teste/seed)."""
        exercicio_com_id = dict(exercicio)
        if exercicio_com_id.get("id") is None:
            exercicio_com_id["id"] = self._proximo_id
            self._proximo_id += 1

        self._exercicios.append(exercicio_com_id)
        return exercicio_com_id

    def listar_todos(self) -> List[Dict[str, Any]]:
        return list(self._exercicios)

    def obter_por_id(self, exercicio_id: int):
        for e in self._exercicios:
            if e.get("id") == exercicio_id:
                return e
        return None


class RepositorioPrescricaoMemoria:
    def __init__(self):
        self._prescricoes: List[Dict[str, Any]] = []

    def proximo_id(self) -> int:
        return len(self._prescricoes) + 1

    def salvar(self, prescricao: Dict[str, Any]) -> None:
        self._prescricoes.append(prescricao)

    def listar_por_paciente(self, paciente_id: str) -> List[Dict[str, Any]]:
        return [p for p in self._prescricoes if p.get("paciente_id") == paciente_id]


# instâncias únicas em memória (iguais ao padrão que vocês já usam)
repo_exercicio_memoria = RepositorioExercicioMemoria()
repo_prescricao_memoria = RepositorioPrescricaoMemoria()

# Alguns exercícios de exemplo pra teste
repo_exercicio_memoria.salvar(
    {
        "nome": "Agachamento Gamificado",
        "nivel_dificuldade": "Médio",
        "descricao": "Agachamentos com contagem automática e feedback visual.",
    }
)
repo_exercicio_memoria.salvar(
    {
        "nome": "Elevação de Pernas Gamificada",
        "nivel_dificuldade": "Fácil",
        "descricao": "Elevação de pernas com metas de tempo.",
    }
)