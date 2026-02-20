"""
NOPAnalyzer — Number of Parents.

Detecta clases que usan herencia múltiple con demasiados padres directos.
NOP > 1 indica que la clase hereda de más de una clase concreta, lo que
complica el MRO (Method Resolution Order) y hace el comportamiento difícil
de predecir.

Nota: un único mixin o base abstracta adicional puede ser aceptable según el
diseño. El umbral es configurable para ajustarlo al contexto del proyecto.

Fecha de creación: 2026-02-20
Ticket: 3.4 + 3.5
"""

import ast
from pathlib import Path
from typing import Any, List

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

# Bases que no cuentan como "padre real" porque son abstractas/protocolo por convención
_BASES_EXCLUIDAS = {"object", "ABC", "Protocol"}


class NOPAnalyzer(Verifiable):
    """
    Detecta clases con herencia múltiple excesiva (NOP alto).

    NOP (Number of Parents) = número de clases base directas de una clase,
    excluyendo `object`, `ABC` y `Protocol`.

    - NOP = 0 o 1 → herencia simple o sin herencia (correcto)
    - NOP > 1     → herencia múltiple (complica MRO, dificulta comprensión)

    Umbral por defecto: 1 (configurable vía max_nop en pyproject.toml).
    Severidad: CRITICAL.
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "NOPAnalyzer"

    @property
    def category(self) -> str:
        return "inheritance"

    @property
    def estimated_duration(self) -> float:
        return 0.3

    @property
    def priority(self) -> int:
        return 2

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        """
        Analiza el archivo y retorna un resultado por cada clase con NOP excesivo.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista de ReviewResult (puede ser vacía si no hay violaciones).
        """
        threshold = self._config.max_nop if self._config else 1
        results: List[ReviewResult] = []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return results

        for nodo in ast.walk(tree):
            if not isinstance(nodo, ast.ClassDef):
                continue

            padres = self._extraer_padres(nodo)
            nop = len(padres)

            if nop > threshold:
                exceso = nop - threshold
                estimated_effort = round(exceso * 1.0, 1)

                results.append(ReviewResult(
                    analyzer_name=self.name,
                    severity=ReviewSeverity.CRITICAL,
                    current_value=nop,
                    threshold=threshold,
                    message=(
                        f"Clase '{nodo.name}' hereda de {nop} clases directas "
                        f"(umbral: {threshold}): {', '.join(padres)}."
                    ),
                    file_path=file_path,
                    class_name=nodo.name,
                    suggestion=(
                        f"Reemplazar los {exceso} padre(s) extra por composición: "
                        f"convertir las clases adicionales en atributos inyectados "
                        f"o en mixins con una única responsabilidad bien delimitada."
                    ),
                    estimated_effort=estimated_effort,
                ))

        return results

    def _extraer_padres(self, class_node: ast.ClassDef) -> List[str]:
        """
        Extrae los nombres de las clases base directas, excluyendo object/ABC/Protocol.

        Args:
            class_node: Nodo AST de la definición de clase.

        Returns:
            Lista de nombres de bases (sin duplicados, en orden de aparición).
        """
        padres: List[str] = []
        vistos = set()

        for base in class_node.bases:
            nombre = self._nombre_base(base)
            if nombre and nombre not in _BASES_EXCLUIDAS and nombre not in vistos:
                padres.append(nombre)
                vistos.add(nombre)

        return padres

    def _nombre_base(self, nodo: ast.expr) -> str:
        """Extrae el nombre simple de un nodo base de herencia."""
        if isinstance(nodo, ast.Name):
            return nodo.id
        if isinstance(nodo, ast.Attribute):
            return nodo.attr
        return ""
