"""
Check de código muerto usando vulture.

Detecta funciones, clases y variables que están definidas pero nunca se usan.
"""

import re
import subprocess
from pathlib import Path
from typing import List

from quality_agents.codeguard.agent import CheckResult, Severity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable


class DeadCodeCheck(Verifiable):
    """
    Detecta código muerto usando vulture.

    Encuentra funciones, clases, métodos, atributos y variables que están
    definidos pero nunca se usan. El nivel de confianza de vulture indica
    qué tan seguro es el diagnóstico.

    Configuración:
        - checks.dead_code: bool (habilitado por defecto)
        - min_dead_code_confidence: int (default: 60, rango 0-100)

    Severidad:
        - WARNING: confianza 60-79%
        - ERROR: confianza 80%+

    Prioridad: 4
    Duración estimada: 1.5s
    """

    @property
    def name(self) -> str:
        return "DeadCode"

    @property
    def category(self) -> str:
        return "quality"

    @property
    def estimated_duration(self) -> float:
        return 1.5

    @property
    def priority(self) -> int:
        return 4

    def should_run(self, context: ExecutionContext) -> bool:
        if context.is_excluded:
            return False
        if context.file_path.suffix != ".py":
            return False
        if context.config and not context.config.checks.dead_code:
            return False
        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        results = []

        min_confidence = 60
        if hasattr(self, "_context") and self._context.config:
            min_confidence = self._context.config.min_dead_code_confidence

        try:
            process = subprocess.run(
                ["vulture", str(file_path), f"--min-confidence={min_confidence}"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            findings = self._parse_vulture_output(process.stdout)

            if not findings:
                results.append(
                    CheckResult(
                        check_name=self.name,
                        severity=Severity.INFO,
                        message="✓ No dead code detected",
                        file_path=str(file_path),
                    )
                )
            else:
                for finding in findings:
                    severity = Severity.ERROR if finding["confidence"] >= 80 else Severity.WARNING
                    results.append(
                        CheckResult(
                            check_name=self.name,
                            severity=severity,
                            message=(
                                f"Dead code: {finding['kind']} '{finding['name']}' "
                                f"is never used ({finding['confidence']}% confidence)"
                            ),
                            file_path=str(file_path),
                            line_number=finding["line"],
                        )
                    )

        except FileNotFoundError:
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="vulture not installed. Run: pip install vulture",
                    file_path=str(file_path),
                )
            )
        except subprocess.TimeoutExpired:
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="vulture execution timed out (>10s)",
                    file_path=str(file_path),
                )
            )
        except Exception as e:
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message=f"Unexpected error running vulture: {str(e)}",
                    file_path=str(file_path),
                )
            )

        return results

    def _parse_vulture_output(self, output: str) -> List[dict]:
        """
        Parsea el output de vulture.

        Formato: <file>:<line>: unused <kind> '<name>' (<confidence>% confidence)
        Ejemplo: sample.py:10: unused function 'my_func' (60% confidence)
        """
        findings = []
        pattern = r"^.+:(\d+): unused (\w+(?: \w+)?) '(.+?)' \((\d+)% confidence\)"

        for line in output.splitlines():
            match = re.match(pattern, line)
            if match:
                findings.append(
                    {
                        "line": int(match.group(1)),
                        "kind": match.group(2),
                        "name": match.group(3),
                        "confidence": int(match.group(4)),
                    }
                )

        return findings
