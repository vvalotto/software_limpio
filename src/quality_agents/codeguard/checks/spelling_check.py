"""
Check de ortografía usando codespell.

Detecta typos en nombres de variables, funciones, comentarios y strings.
"""

import re
import subprocess
from pathlib import Path
from typing import List

from quality_agents.codeguard.agent import CheckResult, Severity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable


class SpellingCheck(Verifiable):
    """
    Detecta typos en código y comentarios usando codespell.

    Analiza nombres de variables, funciones, clases, comentarios y strings
    en busca de palabras mal escritas. Todos los hallazgos se reportan como
    WARNING — los typos son problemas de calidad, no errores críticos.

    Configuración:
        - checks.spelling: bool (habilitado por defecto)
        - spelling_ignore_words: List[str] (palabras a ignorar, default: [])

    Prioridad: 5
    Duración estimada: 1.0s
    """

    @property
    def name(self) -> str:
        return "Spelling"

    @property
    def category(self) -> str:
        return "style"

    @property
    def estimated_duration(self) -> float:
        return 1.0

    @property
    def priority(self) -> int:
        return 5

    def should_run(self, context: ExecutionContext) -> bool:
        if context.is_excluded:
            return False
        if context.file_path.suffix != ".py":
            return False
        if context.config and not context.config.checks.spelling:
            return False
        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        results = []

        ignore_words: List[str] = []
        if hasattr(self, "_context") and self._context.config:
            ignore_words = self._context.config.spelling_ignore_words

        cmd = ["codespell", str(file_path)]
        if ignore_words:
            cmd += ["-L", ",".join(ignore_words)]

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )

            findings = self._parse_codespell_output(process.stdout + process.stderr)

            if not findings:
                results.append(
                    CheckResult(
                        check_name=self.name,
                        severity=Severity.INFO,
                        message="✓ No spelling errors detected",
                        file_path=str(file_path),
                    )
                )
            else:
                for finding in findings:
                    results.append(
                        CheckResult(
                            check_name=self.name,
                            severity=Severity.WARNING,
                            message=(
                                f"Spelling: '{finding['typo']}' should be '{finding['correction']}'"
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
                    message="codespell not installed. Run: pip install codespell",
                    file_path=str(file_path),
                )
            )
        except subprocess.TimeoutExpired:
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="codespell execution timed out (>10s)",
                    file_path=str(file_path),
                )
            )
        except Exception as e:
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message=f"Unexpected error running codespell: {str(e)}",
                    file_path=str(file_path),
                )
            )

        return results

    def _parse_codespell_output(self, output: str) -> List[dict]:
        """
        Parsea el output de codespell.

        Formato: <file>:<line>: <typo> ==> <correction>
        Ejemplo: sample.py:10: calcualte ==> calculate
        """
        findings = []
        pattern = r"^.+:(\d+): (\S+) ==> (\S+)"

        for line in output.splitlines():
            match = re.match(pattern, line)
            if match:
                findings.append(
                    {
                        "line": int(match.group(1)),
                        "typo": match.group(2),
                        "correction": match.group(3),
                    }
                )

        return findings
