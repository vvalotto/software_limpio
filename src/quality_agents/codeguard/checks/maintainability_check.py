"""
Check de Maintainability Index usando radon mi.

Calcula el índice de mantenibilidad (MI) de cada archivo, una métrica compuesta
que combina complejidad ciclomática, volumen de Halstead y líneas de código.
"""

import json
import subprocess
from pathlib import Path
from typing import List

from quality_agents.codeguard.agent import CheckResult, Severity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable


class MaintainabilityCheck(Verifiable):
    """
    Detecta archivos con bajo índice de mantenibilidad usando radon mi.

    El Maintainability Index (MI) combina complejidad ciclomática, volumen de
    Halstead y líneas de código en un único score (0-100). Radon lo clasifica en:

        A: MI >= 20  (fácil de mantener)
        B: MI 10-19  (moderadamente mantenible)
        C: MI < 10   (difícil de mantener)

    Configuración:
        - checks.maintainability: bool (habilitado por defecto)
        - min_maintainability_index: int (default: 20 — por debajo emite WARNING/ERROR)

    Severidad:
        - INFO:    MI >= min_maintainability_index (grado A con umbral default)
        - WARNING: MI entre 10 y min_maintainability_index
        - ERROR:   MI < 10 (grado C)

    Prioridad: 4
    Duración estimada: 1.0s
    """

    @property
    def name(self) -> str:
        return "Maintainability"

    @property
    def category(self) -> str:
        return "complexity"

    @property
    def estimated_duration(self) -> float:
        return 1.0

    @property
    def priority(self) -> int:
        return 4

    def should_run(self, context: ExecutionContext) -> bool:
        if context.is_excluded:
            return False
        if context.file_path.suffix != ".py":
            return False
        if context.config and not context.config.checks.maintainability:
            return False
        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        results = []

        min_mi = 20
        if hasattr(self, "_context") and self._context.config:
            min_mi = self._context.config.min_maintainability_index

        try:
            process = subprocess.run(
                ["radon", "mi", "-s", "-j", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            mi_value, rank = self._parse_radon_output(process.stdout, str(file_path))

            if mi_value is None:
                results.append(
                    CheckResult(
                        check_name=self.name,
                        severity=Severity.INFO,
                        message="✓ Maintainability index could not be calculated (file may be empty)",
                        file_path=str(file_path),
                    )
                )
            elif mi_value >= min_mi:
                results.append(
                    CheckResult(
                        check_name=self.name,
                        severity=Severity.INFO,
                        message=f"✓ Maintainability index: {mi_value:.1f} (grade {rank})",
                        file_path=str(file_path),
                    )
                )
            else:
                severity = Severity.ERROR if mi_value < 10 else Severity.WARNING
                results.append(
                    CheckResult(
                        check_name=self.name,
                        severity=severity,
                        message=(
                            f"Low maintainability: MI={mi_value:.1f} (grade {rank}, "
                            f"threshold={min_mi}). Consider reducing complexity or splitting the file."
                        ),
                        file_path=str(file_path),
                    )
                )

        except FileNotFoundError:
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="radon not installed. Run: pip install radon",
                    file_path=str(file_path),
                )
            )
        except subprocess.TimeoutExpired:
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="radon execution timed out (>10s)",
                    file_path=str(file_path),
                )
            )
        except Exception as e:
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message=f"Unexpected error running radon: {str(e)}",
                    file_path=str(file_path),
                )
            )

        return results

    def _parse_radon_output(self, output: str, file_path: str) -> tuple:
        """
        Parsea el output JSON de radon mi -s -j.

        Formato: {"path": {"mi": float, "rank": "A/B/C"}}

        Retorna (mi_value, rank) o (None, None) si no hay datos.
        """
        if not output.strip():
            return None, None

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return None, None

        # radon usa la ruta tal como se la pasamos como clave
        if not data:
            return None, None

        # Tomar el primer (y único) resultado
        entry = next(iter(data.values()))
        return entry.get("mi"), entry.get("rank")
