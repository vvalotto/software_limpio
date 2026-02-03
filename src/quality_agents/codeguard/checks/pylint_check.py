"""
Check de calidad usando pylint.

Este check ejecuta pylint para analizar calidad de código y obtiene
un score de 0-10. Verifica que el score sea >= min_score configurado.

Fecha de creación: 2026-02-03
Ticket: 2.2
"""

import re
import subprocess
from pathlib import Path
from typing import List

from quality_agents.shared.verifiable import ExecutionContext, Verifiable
from quality_agents.codeguard.agent import CheckResult, Severity


class PylintCheck(Verifiable):
    """
    Verifica calidad de código usando pylint.

    Ejecuta pylint para obtener un score de calidad (0-10) y verifica
    que sea mayor o igual al umbral configurado (default: 8.0).

    Pylint analiza:
    - Errores de sintaxis y lógica
    - Convenciones de código
    - Duplicación de código
    - Complejidad
    - Malas prácticas

    Configuración:
        - check_pylint: bool (habilitado por defecto)
        - min_pylint_score: float (default: 8.0)

    Prioridad: 4 (Media - análisis profundo pero no crítico)
    Duración estimada: 2.0s (más lento que flake8)
    """

    @property
    def name(self) -> str:
        """Nombre identificador del check."""
        return "Pylint"

    @property
    def category(self) -> str:
        """Categoría del check."""
        return "quality"

    @property
    def estimated_duration(self) -> float:
        """Duración estimada en segundos."""
        return 2.0

    @property
    def priority(self) -> int:
        """Prioridad de ejecución (1=más alta, 10=más baja)."""
        return 4

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
        if context.config and not context.config.check_pylint:
            return False

        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        """
        Ejecuta pylint sobre el archivo.

        Args:
            file_path: Ruta al archivo Python

        Returns:
            Lista de resultados de verificación
        """
        results = []

        try:
            # Ejecutar pylint con score-only para obtener solo la puntuación
            # Usamos --score=y para asegurar que se muestre el score
            process = subprocess.run(
                ["pylint", "--score=y", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10,  # Pylint puede ser más lento
            )

            # Extraer score del output
            # Formato: "Your code has been rated at X.XX/10"
            score = self._extract_score(process.stdout)

            if score is not None:
                # Obtener min_score de config o usar default
                min_score = 8.0
                if hasattr(self, "_context") and self._context and self._context.config:
                    min_score = self._context.config.min_pylint_score

                if score >= min_score:
                    results.append(
                        CheckResult(
                            check_name=self.name,
                            severity=Severity.INFO,
                            message=f"✓ Pylint score: {score:.2f}/10 (>= {min_score})",
                            file_path=str(file_path),
                        )
                    )
                else:
                    results.append(
                        CheckResult(
                            check_name=self.name,
                            severity=Severity.WARNING,
                            message=f"⚠ Pylint score: {score:.2f}/10 (< {min_score}). "
                            f"Run 'pylint {file_path.name}' for details.",
                            file_path=str(file_path),
                        )
                    )
            else:
                # No se pudo extraer score
                results.append(
                    CheckResult(
                        check_name=self.name,
                        severity=Severity.ERROR,
                        message="Could not extract pylint score from output",
                        file_path=str(file_path),
                    )
                )

        except FileNotFoundError:
            # pylint no instalado
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="pylint not installed. Run: pip install pylint",
                    file_path=str(file_path),
                )
            )
        except subprocess.TimeoutExpired:
            # Timeout
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="pylint execution timed out (>10s)",
                    file_path=str(file_path),
                )
            )
        except Exception as e:
            # Error inesperado
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message=f"Unexpected error running pylint: {str(e)}",
                    file_path=str(file_path),
                )
            )

        return results

    def _extract_score(self, output: str) -> float | None:
        """
        Extrae el score de pylint del output.

        Args:
            output: Output de pylint

        Returns:
            Score (0-10) o None si no se pudo extraer
        """
        # Buscar patrón: "Your code has been rated at X.XX/10"
        match = re.search(r"rated at ([\d.]+)/10", output)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None
