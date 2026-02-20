"""
DataClumpsAnalyzer — Detección de Data Clumps (datos que viajan juntos).

Un Data Clump ocurre cuando el mismo grupo de parámetros aparece repetidamente
en múltiples funciones o métodos de un archivo. Indica que esos datos forman una
abstracción cohesiva que debería encapsularse en una clase o dataclass.

Viola el principio SRP: la dispersión del mismo grupo de datos en múltiples firmas
de función sugiere que falta una abstracción de dominio.

Algoritmo:
1. Recolectar los conjuntos de parámetros de todas las funciones del archivo.
2. Generar todos los subconjuntos de tamaño >= min_data_clump_size.
3. Contar en cuántas funciones distintas aparece cada subconjunto.
4. Reportar los subconjuntos con >= min_data_clump_occurrences apariciones.
5. Solo reportar clumps máximos: si el clump {a, b, c} ya está reportado,
   no reportar el sub-clump {a, b}.

Fecha de creación: 2026-02-20
Ticket: 4.5
"""

import ast
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity, SolidPrinciple
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

# Parámetros implícitos que no forman parte de clumps de negocio
_PARAMS_EXCLUIDOS: Set[str] = {"self", "cls"}


class DataClumpsAnalyzer(Verifiable):
    """
    Detecta grupos de parámetros que siempre aparecen juntos en múltiples funciones.

    Un grupo de parámetros es un Data Clump si:
    - Tiene al menos min_data_clump_size parámetros (default: 3)
    - Aparece en al menos min_data_clump_occurrences funciones distintas (default: 2)

    Solo se reportan clumps máximos: si {a, b, c, d} ya está reportado como clump,
    no se reporta el sub-clump {a, b, c} aunque también cumpla las condiciones.
    Esto evita alertas redundantes sobre el mismo problema.

    Severidad: WARNING (viola SRP).
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "DataClumpsAnalyzer"

    @property
    def category(self) -> str:
        return "smells"

    @property
    def estimated_duration(self) -> float:
        return 0.8

    @property
    def priority(self) -> int:
        return 3

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        """
        Analiza el archivo y retorna un resultado por cada Data Clump detectado.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista de ReviewResult (puede ser vacía si no hay violaciones).
        """
        min_size = self._config.min_data_clump_size if self._config else 3
        min_occurrences = self._config.min_data_clump_occurrences if self._config else 2
        results: List[ReviewResult] = []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return results

        firmas = self._recolectar_firmas(tree, min_size)
        if len(firmas) < min_occurrences:
            return results  # No hay suficientes funciones para formar un clump

        clumps = self._encontrar_clumps(firmas, min_size, min_occurrences)

        for clump, funciones in clumps:
            params_str = ", ".join(sorted(clump))
            n_funcs = len(funciones)
            funcs_str = ", ".join(f"'{f}'" for f in sorted(funciones))

            results.append(ReviewResult(
                analyzer_name=self.name,
                severity=ReviewSeverity.WARNING,
                current_value=n_funcs,
                threshold=min_occurrences,
                message=(
                    f"Data Clump: parámetros {{{params_str}}} aparecen juntos "
                    f"en {n_funcs} funciones ({funcs_str})."
                ),
                file_path=file_path,
                class_name=None,
                suggestion=(
                    f"Crear una dataclass o namedtuple con los campos "
                    f"{{{params_str}}} y usarla como parámetro único."
                ),
                estimated_effort=2.0,
                solid_principle=SolidPrinciple.SRP,
                smell_type="DataClumps",
            ))

        return results

    def _recolectar_firmas(
        self, tree: ast.Module, min_size: int
    ) -> List[Tuple[str, FrozenSet[str]]]:
        """
        Recolecta (nombre_función, frozenset_params) de todas las funciones del archivo.

        Solo incluye funciones con al menos min_size parámetros (excluyendo self/cls).
        Analiza funciones de módulo y métodos de clase (no funciones anidadas).
        """
        firmas: List[Tuple[str, FrozenSet[str]]] = []
        self._recolectar_scope(tree.body, firmas, min_size, class_name=None)
        return firmas

    def _recolectar_scope(
        self,
        nodos: list,
        firmas: List[Tuple[str, FrozenSet[str]]],
        min_size: int,
        class_name: Optional[str],
    ) -> None:
        """Recorre nodos AST recolectando firmas de funciones y métodos."""
        for nodo in nodos:
            if isinstance(nodo, ast.ClassDef):
                self._recolectar_scope(nodo.body, firmas, min_size, class_name=nodo.name)
            elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                params = self._obtener_params(nodo)
                if len(params) >= min_size:
                    nombre = f"{class_name}.{nodo.name}" if class_name else nodo.name
                    firmas.append((nombre, frozenset(params)))

    def _obtener_params(self, func_node: ast.FunctionDef) -> List[str]:
        """
        Retorna los parámetros de la función excluyendo self, cls, *args y **kwargs.
        """
        args = func_node.args
        todos = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
        return [a.arg for a in todos if a.arg not in _PARAMS_EXCLUIDOS]

    def _encontrar_clumps(
        self,
        firmas: List[Tuple[str, FrozenSet[str]]],
        min_size: int,
        min_occurrences: int,
    ) -> List[Tuple[FrozenSet[str], Set[str]]]:
        """
        Detecta todos los clumps máximos que cumplen las condiciones.

        Pasos:
        1. Generar todos los subconjuntos de tamaño >= min_size de cada firma.
        2. Contar en cuántas funciones distintas aparece cada subconjunto.
        3. Filtrar los que aparecen en >= min_occurrences funciones.
        4. Eliminar sub-clumps: si {a,b,c,d} es un clump válido, omitir {a,b,c}.

        Returns:
            Lista de (clump, set_de_funciones) ordenada de mayor a menor tamaño.
        """
        # Paso 1 y 2: contar apariciones por subconjunto
        conteo: Dict[FrozenSet[str], Set[str]] = defaultdict(set)

        for nombre, params in firmas:
            max_size = len(params)
            for size in range(min_size, max_size + 1):
                for combo in combinations(sorted(params), size):
                    conteo[frozenset(combo)].add(nombre)

        # Paso 3: filtrar por min_occurrences
        candidatos = {
            clump: funcs
            for clump, funcs in conteo.items()
            if len(funcs) >= min_occurrences
        }

        if not candidatos:
            return []

        # Paso 4: conservar solo clumps máximos (no sub-clumps de uno ya seleccionado)
        clumps_ordenados = sorted(candidatos.keys(), key=len, reverse=True)
        seleccionados: List[FrozenSet[str]] = []

        for clump in clumps_ordenados:
            es_subclump = any(clump < mayor for mayor in seleccionados)
            if not es_subclump:
                seleccionados.append(clump)

        return [(clump, candidatos[clump]) for clump in seleccionados]
