"""
LongMethodAnalyzer — Detección de métodos demasiado largos.

Un método largo es una señal de que hace demasiadas cosas: viola SRP.
Se detecta midiendo las líneas de código desde la definición (def)
hasta el final del cuerpo (end_lineno).

Aplica tanto a métodos de clase como a funciones de módulo.

Fecha de creación: 2026-02-20
Ticket: 4.2
"""

import ast
from pathlib import Path
from typing import Any, List, Optional, Union

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity, SolidPrinciple
from quality_agents.shared.verifiable import ExecutionContext, Verifiable


class LongMethodAnalyzer(Verifiable):
    """
    Detecta métodos y funciones con demasiadas líneas de código.

    Un método que supera max_method_lines líneas probablemente hace más de una
    cosa (viola SRP). La longitud se mide desde la línea de la definición (def)
    hasta la última línea del cuerpo (end_lineno), inclusive.

    Analiza métodos de clase y funciones de módulo. Para clases anidadas,
    los métodos se reportan con el nombre de la clase más próxima como contexto.

    Umbral por defecto: 20 líneas (configurable vía max_method_lines en pyproject.toml).
    Severidad: WARNING (viola SRP).
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "LongMethodAnalyzer"

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
        Analiza el archivo y retorna un resultado por cada método o función larga.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista de ReviewResult (puede ser vacía si no hay violaciones).
        """
        threshold = self._config.max_method_lines if self._config else 20
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

        Para clases, recursa en sus métodos usando el nombre de la clase como contexto.
        Para funciones, evalúa el largo y recursa para detectar funciones anidadas.
        """
        for nodo in nodos:
            if isinstance(nodo, ast.ClassDef):
                self._analizar_scope(
                    nodo.body, file_path, threshold, results, class_name=nodo.name
                )
            elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._evaluar_funcion(nodo, file_path, threshold, results, class_name)
                # Recursar para detectar funciones anidadas dentro de la función
                self._analizar_scope(
                    nodo.body, file_path, threshold, results, class_name=class_name
                )

    def _evaluar_funcion(
        self,
        func: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        file_path: Path,
        threshold: int,
        results: List[ReviewResult],
        class_name: Optional[str],
    ) -> None:
        """Evalúa una función y agrega un resultado si supera el umbral."""
        lineas = (func.end_lineno or func.lineno) - func.lineno + 1
        if lineas <= threshold:
            return

        exceso = lineas - threshold
        estimated_effort = round(exceso / 10 * 0.5, 1)
        nombre_completo = f"{class_name}.{func.name}" if class_name else func.name

        results.append(ReviewResult(
            analyzer_name=self.name,
            severity=ReviewSeverity.WARNING,
            current_value=lineas,
            threshold=threshold,
            message=(
                f"Método '{nombre_completo}' tiene {lineas} líneas "
                f"(umbral: {threshold}). Método demasiado largo."
            ),
            file_path=file_path,
            class_name=class_name,
            suggestion=(
                f"Extraer {exceso} línea(s) en métodos auxiliares con nombres descriptivos."
            ),
            estimated_effort=estimated_effort,
            solid_principle=SolidPrinciple.SRP,
            smell_type="LongMethod",
        ))
