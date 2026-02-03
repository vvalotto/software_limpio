"""
Check PEP8 usando flake8.

Este check verifica conformidad con PEP8 (Python Enhancement Proposal 8),
la guía de estilo oficial de Python.

Fecha de creación: 2026-02-03
Ticket: 2.1
"""

import subprocess
from pathlib import Path
from typing import List

from quality_agents.shared.verifiable import ExecutionContext, Verifiable
from quality_agents.codeguard.agent import CheckResult, Severity


class PEP8Check(Verifiable):
    """
    Verifica conformidad con PEP8 usando flake8.

    Ejecuta flake8 para detectar violaciones de estilo según PEP8:
    - Longitud de línea
    - Indentación
    - Espacios en blanco
    - Importaciones
    - Convenciones de nombres

    Configuración:
        - check_pep8: bool (habilitado por defecto)
        - max_line_length: int (default: 100)

    Prioridad: 2 (Alta - estilo es importante)
    Duración estimada: 0.5s
    """

    @property
    def name(self) -> str:
        """Nombre identificador del check."""
        return "PEP8"

    @property
    def category(self) -> str:
        """Categoría del check."""
        return "style"

    @property
    def estimated_duration(self) -> float:
        """Duración estimada en segundos."""
        return 0.5

    @property
    def priority(self) -> int:
        """Prioridad de ejecución (1=más alta, 10=más baja)."""
        return 2

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
        if context.config and not context.config.check_pep8:
            return False

        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        """
        Ejecuta flake8 sobre el archivo.

        Args:
            file_path: Ruta al archivo Python

        Returns:
            Lista de resultados de verificación
        """
        results = []

        try:
            # Ejecutar flake8 con formato parseable
            # --max-line-length se puede configurar desde config
            process = subprocess.run(
                ["flake8", "--max-line-length=100", str(file_path)],
                capture_output=True,
                text=True,
                timeout=5,
            )

            # flake8 retorna exit code 0 si no hay errores
            if process.returncode == 0 and not process.stdout.strip():
                # Sin errores PEP8
                results.append(
                    CheckResult(
                        check_name=self.name,
                        severity=Severity.INFO,
                        message="✓ PEP8 compliant",
                        file_path=str(file_path),
                    )
                )
            else:
                # Parsear errores
                for line in process.stdout.strip().split("\n"):
                    if not line.strip():
                        continue

                    # Formato flake8: file.py:line:col: code message
                    parts = line.split(":", 3)
                    if len(parts) >= 4:
                        line_num = int(parts[1])
                        error_code = parts[3].strip().split()[0]
                        message = parts[3].strip()

                        results.append(
                            CheckResult(
                                check_name=self.name,
                                severity=Severity.WARNING,
                                message=f"PEP8: {message}",
                                file_path=str(file_path),
                                line_number=line_num,
                            )
                        )

        except FileNotFoundError:
            # flake8 no instalado
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="flake8 not installed. Run: pip install flake8",
                    file_path=str(file_path),
                )
            )
        except subprocess.TimeoutExpired:
            # Timeout
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="flake8 execution timed out (>5s)",
                    file_path=str(file_path),
                )
            )
        except Exception as e:
            # Error inesperado
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message=f"Unexpected error running flake8: {str(e)}",
                    file_path=str(file_path),
                )
            )

        return results
