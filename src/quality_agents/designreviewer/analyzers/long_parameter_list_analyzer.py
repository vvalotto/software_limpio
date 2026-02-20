"""
LongParameterListAnalyzer — Detección de listas de parámetros excesivamente largas.

Una función con demasiados parámetros es difícil de llamar, testear y mantener.
Indica que la función probablemente hace demasiadas cosas o que los parámetros
deberían agruparse en un objeto (Parameter Object).

Viola el principio ISP (Interface Segregation Principle): una interfaz con
demasiados parámetros obliga a los clientes a conocer y proveer más datos de
los que necesitan.

Fecha de creación: 2026-02-20
Ticket: 4.3
"""

import ast
from pathlib import Path
from typing import Any, List, Optional

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity, SolidPrinciple
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

# Parámetros implícitos que se excluyen del conteo
_PARAMS_EXCLUIDOS = {"self", "cls"}


class LongParameterListAnalyzer(Verifiable):
    """
    Detecta funciones y métodos con demasiados parámetros.

    Cuenta todos los parámetros declarados explícitamente, excluyendo 'self' y 'cls'.
    No cuenta *args ni **kwargs como parámetros adicionales (son mecanismos de
    variabilidad, no parámetros de negocio).

    Parámetros contados:
    - args.posonlyargs: parámetros solo-posicionales (antes de /)
    - args.args: parámetros posicionales normales (excluyendo self/cls)
    - args.kwonlyargs: parámetros solo-keyword (después de *)

    Umbral por defecto: 5 parámetros (configurable vía max_parameters en pyproject.toml).
    Severidad: WARNING (viola ISP).
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "LongParameterListAnalyzer"

    @property
    def category(self) -> str:
        return "smells"

    @property
    def estimated_duration(self) -> float:
        return 0.5

    @property
    def priority(self) -> int:
        return 2

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        """
        Analiza el archivo y retorna un resultado por cada función con demasiados parámetros.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista de ReviewResult (puede ser vacía si no hay violaciones).
        """
        threshold = self._config.max_parameters if self._config else 5
        results: List[ReviewResult] = []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return results

        self._analizar_scope(tree.body, file_path, threshold, results, class_name=None)
        return results

    def _analizar_scope(
        self,
        nodos: list,
        file_path: Path,
        threshold: int,
        results: List[ReviewResult],
        class_name: Optional[str],
    ) -> None:
        """
        Analiza funciones y clases en una lista de nodos AST de forma recursiva.
        """
        for nodo in nodos:
            if isinstance(nodo, ast.ClassDef):
                self._analizar_scope(
                    nodo.body, file_path, threshold, results, class_name=nodo.name
                )
            elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._evaluar_funcion(nodo, file_path, threshold, results, class_name)
                self._analizar_scope(
                    nodo.body, file_path, threshold, results, class_name=class_name
                )

    def _evaluar_funcion(
        self,
        func: ast.FunctionDef,
        file_path: Path,
        threshold: int,
        results: List[ReviewResult],
        class_name: Optional[str],
    ) -> None:
        """Evalúa una función y agrega un resultado si supera el umbral de parámetros."""
        cantidad = self._contar_parametros(func)
        if cantidad <= threshold:
            return

        exceso = cantidad - threshold
        estimated_effort = round(exceso * 0.5, 1)
        nombre_completo = f"{class_name}.{func.name}" if class_name else func.name

        results.append(ReviewResult(
            analyzer_name=self.name,
            severity=ReviewSeverity.WARNING,
            current_value=cantidad,
            threshold=threshold,
            message=(
                f"Función '{nombre_completo}' tiene {cantidad} parámetros "
                f"(umbral: {threshold}). Lista de parámetros demasiado larga."
            ),
            file_path=file_path,
            class_name=class_name,
            suggestion=(
                f"Agrupar los {cantidad} parámetros en un objeto Parameter Object o dataclass."
            ),
            estimated_effort=estimated_effort,
            solid_principle=SolidPrinciple.ISP,
            smell_type="LongParameterList",
        ))

    def _contar_parametros(self, func: ast.FunctionDef) -> int:
        """
        Cuenta los parámetros explícitos de la función, excluyendo self/cls, *args y **kwargs.

        Incluye:
        - Parámetros solo-posicionales (posonlyargs)
        - Parámetros posicionales normales (args), excluyendo self/cls
        - Parámetros solo-keyword (kwonlyargs)

        No incluye:
        - vararg (*args): mecanismo de variabilidad, no parámetro de negocio
        - kwarg (**kwargs): ídem
        """
        args = func.args
        todos = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
        return sum(1 for a in todos if a.arg not in _PARAMS_EXCLUIDOS)
