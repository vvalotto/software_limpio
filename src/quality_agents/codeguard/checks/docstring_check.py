"""
Check de cobertura de docstrings usando el módulo ast de la stdlib.

Mide la documentación del código (PEP 257) como una preocupación propia de
CodeGuard, en vez de dejarla diluida dentro del score compuesto de pylint.

Fecha de creación: 2026-09-02
Issue: #69
"""

import ast
from pathlib import Path
from typing import List

from quality_agents.codeguard.agent import CheckResult, Severity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

# Cantidad de símbolos sin docstring a listar por nombre en el mensaje
_MAX_MISSING_NAMES = 5


class DocstringCheck(Verifiable):
    """
    Mide la cobertura de docstrings de un archivo Python usando `ast`.

    Símbolos documentables: el módulo, cada clase y cada función/método
    (sync o async), sin excluir símbolos privados (prefijo `_`) — a
    diferencia de pylint, que por convención puede tratarlos distinto.

    Configuración:
        - check_docstrings: bool (habilitado por defecto)
        - min_docstring_coverage: float, porcentaje mínimo (default: 80.0)

    Prioridad: 3 (Alta - corre en modo pre-commit)
    Duración estimada: 0.5s (análisis AST puro, sin subprocess)
    """

    @property
    def name(self) -> str:
        """Nombre identificador del check."""
        return "Docstrings"

    @property
    def category(self) -> str:
        """Categoría del check."""
        return "documentation"

    @property
    def estimated_duration(self) -> float:
        """Duración estimada en segundos."""
        return 0.5

    @property
    def priority(self) -> int:
        """Prioridad de ejecución (1=más alta, 10=más baja)."""
        return 3

    def should_run(self, context: ExecutionContext) -> bool:
        """
        Determina si debe ejecutarse en este contexto.

        Args:
            context: Contexto de ejecución

        Returns:
            True si debe ejecutarse, False en caso contrario
        """
        # Archivo excluido
        if context.is_excluded:
            return False

        # Solo archivos Python
        if context.file_path.suffix != ".py":
            return False

        # Verificar si está habilitado en config
        if context.config and not context.config.checks.docstrings:
            return False

        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        """
        Analiza el archivo con `ast` y calcula la cobertura de docstrings.

        Args:
            file_path: Ruta al archivo Python

        Returns:
            Lista de resultados de verificación (un único CheckResult)
        """
        min_coverage = 80.0
        if hasattr(self, "_context") and self._context and self._context.config:
            min_coverage = self._context.config.min_docstring_coverage

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as e:
            return [
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message=f"Could not parse file for docstring analysis: {e}",
                    file_path=str(file_path),
                )
            ]
        except Exception as e:
            return [
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message=f"Unexpected error analyzing docstrings: {str(e)}",
                    file_path=str(file_path),
                )
            ]

        symbols = self._collect_symbols(tree)

        # `_collect_symbols` siempre incluye el módulo, así que `symbols`
        # nunca está vacío (incluso un archivo trivial es "documentable").
        documented = [s for s in symbols if s["has_docstring"]]
        coverage = (len(documented) / len(symbols)) * 100

        if coverage >= min_coverage:
            return [
                CheckResult(
                    check_name=self.name,
                    severity=Severity.INFO,
                    message=(
                        f"✓ Docstring coverage {coverage:.1f}% "
                        f"({len(documented)}/{len(symbols)}) meets threshold (≥{min_coverage}%)"
                    ),
                    file_path=str(file_path),
                )
            ]

        missing = [s for s in symbols if not s["has_docstring"]]
        missing_names = ", ".join(s["name"] for s in missing[:_MAX_MISSING_NAMES])
        remaining = len(missing) - _MAX_MISSING_NAMES
        more = f" (+{remaining} more)" if remaining > 0 else ""

        return [
            CheckResult(
                check_name=self.name,
                severity=Severity.WARNING,
                message=(
                    f"Docstring coverage {coverage:.1f}% "
                    f"({len(documented)}/{len(symbols)}) below threshold (≥{min_coverage}%). "
                    f"Missing: {missing_names}{more}"
                ),
                file_path=str(file_path),
                line_number=missing[0]["line"],
            )
        ]

    def _collect_symbols(self, tree: ast.Module) -> List[dict]:
        """
        Recolecta todos los símbolos documentables del árbol AST.

        Incluye el módulo, todas las clases y todas las funciones/métodos
        (sync o async), sin excepción para símbolos privados.

        Args:
            tree: Árbol AST del archivo (raíz `ast.Module`)

        Returns:
            Lista de dicts con `name`, `line` y `has_docstring`
        """
        symbols = [
            {
                "name": "<module>",
                "line": 1,
                "has_docstring": ast.get_docstring(tree) is not None,
            }
        ]

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbols.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "has_docstring": ast.get_docstring(node) is not None,
                    }
                )

        return symbols
