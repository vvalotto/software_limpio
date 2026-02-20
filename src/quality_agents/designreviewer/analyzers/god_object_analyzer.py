"""
GodObjectAnalyzer — Detección de God Object (clase dios).

Detecta clases que acumulan demasiadas responsabilidades, medidas por:
- Número de métodos públicos > max_god_object_methods (default: 20)
- Número de líneas de la clase > max_god_object_lines (default: 300)

Se reporta si cualquiera de las dos condiciones se cumple.
Viola el principio SRP (Single Responsibility Principle).

Fecha de creación: 2026-02-20
Ticket: 4.2
"""

import ast
from pathlib import Path
from typing import Any, List

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity, SolidPrinciple
from quality_agents.shared.verifiable import ExecutionContext, Verifiable


class GodObjectAnalyzer(Verifiable):
    """
    Detecta clases con demasiadas responsabilidades (God Object).

    Una clase es considerada "God Object" si:
    - Tiene más de max_god_object_methods métodos públicos (no dunder), o
    - Ocupa más de max_god_object_lines líneas de código.

    Se reporta si cualquiera de las dos condiciones se cumple. El valor reportado
    es el de la condición más grave (métodos tiene prioridad sobre líneas).

    Umbrales por defecto: 20 métodos / 300 líneas (configurables vía pyproject.toml).
    Severidad: CRITICAL (viola SRP).
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "GodObjectAnalyzer"

    @property
    def category(self) -> str:
        return "smells"

    @property
    def estimated_duration(self) -> float:
        return 0.5

    @property
    def priority(self) -> int:
        return 1

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        """
        Analiza el archivo y retorna un resultado por cada clase con God Object.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista de ReviewResult (puede ser vacía si no hay violaciones).
        """
        max_methods = self._config.max_god_object_methods if self._config else 20
        max_lines = self._config.max_god_object_lines if self._config else 300
        results: List[ReviewResult] = []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return results

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            n_metodos = self._contar_metodos_publicos(node)
            n_lineas = node.end_lineno - node.lineno + 1  # type: ignore[attr-defined]

            excede_metodos = n_metodos > max_methods
            excede_lineas = n_lineas > max_lines

            if not (excede_metodos or excede_lineas):
                continue

            # Valor reportado: métodos tiene prioridad sobre líneas
            current_value = n_metodos if excede_metodos else n_lineas
            threshold = max_methods if excede_metodos else max_lines

            exceso_metodos = max(0, n_metodos - max_methods)
            exceso_bloques = max(0, n_lineas - max_lines) // 50
            estimated_effort = round(3.0 + (exceso_metodos + exceso_bloques) * 0.5, 1)

            partes = []
            if excede_metodos:
                partes.append(f"{n_metodos} métodos (umbral: {max_methods})")
            if excede_lineas:
                partes.append(f"{n_lineas} líneas (umbral: {max_lines})")

            results.append(ReviewResult(
                analyzer_name=self.name,
                severity=ReviewSeverity.CRITICAL,
                current_value=current_value,
                threshold=threshold,
                message=(
                    f"Clase '{node.name}' tiene {', '.join(partes)}. "
                    f"Clase dios: acumula demasiadas responsabilidades."
                ),
                file_path=file_path,
                class_name=node.name,
                suggestion=(
                    f"Dividir '{node.name}' aplicando SRP: extraer responsabilidades "
                    f"en clases separadas. Esfuerzo estimado: {estimated_effort}h."
                ),
                estimated_effort=estimated_effort,
                solid_principle=SolidPrinciple.SRP,
                smell_type="GodObject",
            ))

        return results

    def _contar_metodos_publicos(self, class_node: ast.ClassDef) -> int:
        """
        Cuenta los métodos que no son dunder (no empiezan con '__').

        Incluye métodos de instancia, estáticos y de clase. Excluye
        métodos dunder como __init__, __str__, etc., ya que son parte
        del protocolo de Python y no indican responsabilidades adicionales.
        """
        return sum(
            1
            for nodo in class_node.body
            if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not nodo.name.startswith("__")
        )
