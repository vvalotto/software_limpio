"""
FanOutAnalyzer — Fan-Out de módulos importados.

Cuenta cuántos módulos externos distintos importa un archivo.
Fan-Out alto indica que el módulo tiene demasiadas dependencias externas,
lo que dificulta el testing aislado y aumenta la fragilidad (viola DIP).

Fecha de creación: 2026-02-19
Ticket: 2.2 + 2.4
"""

import ast
from pathlib import Path
from typing import Any, List, Set

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable


class FanOutAnalyzer(Verifiable):
    """
    Detecta archivos con demasiadas dependencias de módulos externos (Fan-Out alto).

    Fan-Out = número de módulos raíz externos distintos importados por el archivo.
    Se cuentan: `import X` y `from X import Y`, usando el módulo raíz (primer segmento).
    Se excluyen los imports relativos (`from . import ...`, `from .module import ...`).

    Umbral por defecto: 7 (configurable vía max_fan_out en pyproject.toml).
    Severidad: WARNING.
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "FanOutAnalyzer"

    @property
    def category(self) -> str:
        return "coupling"

    @property
    def estimated_duration(self) -> float:
        return 0.3

    @property
    def priority(self) -> int:
        return 3

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        """
        Analiza el archivo y retorna un resultado si el Fan-Out supera el umbral.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista con un ReviewResult si hay violación, vacía si no.
        """
        threshold = self._config.max_fan_out if self._config else 7
        results: List[ReviewResult] = []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return results

        modulos = self._recolectar_modulos(tree)
        fan_out = len(modulos)

        if fan_out > threshold:
            exceso = fan_out - threshold
            estimated_effort = round(exceso * 0.25, 1)

            results.append(ReviewResult(
                analyzer_name=self.name,
                severity=ReviewSeverity.WARNING,
                current_value=fan_out,
                threshold=threshold,
                message=(
                    f"'{file_path.name}' importa {fan_out} módulos externos "
                    f"(umbral: {threshold}). "
                    f"Módulos: {', '.join(sorted(modulos))}."
                ),
                file_path=file_path,
                suggestion=(
                    f"Reducir las {exceso} dependencia(s) extra aplicando Dependency Inversion: "
                    f"agrupar imports relacionados en un módulo facade o usar inyección."
                ),
                estimated_effort=estimated_effort,
            ))

        return results

    def _recolectar_modulos(self, tree: ast.AST) -> Set[str]:
        """
        Recolecta los módulos raíz externos únicos del árbol AST.

        Extrae el primer segmento del nombre de módulo para contar dependencias
        a nivel de paquete raíz (ej: `from os.path import join` → `os`).
        Los imports relativos (level > 0) se ignoran.

        Args:
            tree: AST del archivo a analizar.

        Returns:
            Conjunto de nombres de módulos raíz externos únicos.
        """
        modulos: Set[str] = set()

        for nodo in ast.walk(tree):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    raiz = alias.name.split(".")[0]
                    modulos.add(raiz)

            elif isinstance(nodo, ast.ImportFrom):
                # level > 0 indica import relativo (from . import X)
                if nodo.level == 0 and nodo.module:
                    raiz = nodo.module.split(".")[0]
                    modulos.add(raiz)

        return modulos
