"""
Check de seguridad usando bandit.

Este check detecta vulnerabilidades de seguridad comunes en código Python
usando bandit, una herramienta de análisis de seguridad estático.

Fecha de creación: 2026-02-03
Ticket: 2.3
"""

import json
import subprocess
from pathlib import Path
from typing import List

from quality_agents.codeguard.agent import CheckResult, Severity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable


class SecurityCheck(Verifiable):
    """
    Detecta vulnerabilidades de seguridad usando bandit.

    Ejecuta bandit para identificar problemas de seguridad comunes:
    - Hardcoded passwords/secrets
    - SQL injection patterns
    - Use of eval/exec
    - Weak cryptography
    - Insecure deserialization
    - Shell injection
    - Path traversal

    Severidades bandit → CodeGuard:
        HIGH → ERROR (crítico, debe corregirse)
        MEDIUM → WARNING (importante, revisar)
        LOW → INFO (informativo)

    Configuración:
        - check_security: bool (habilitado por defecto)

    Prioridad: 1 (Máxima - seguridad es crítica)
    Duración estimada: 1.5s
    """

    @property
    def name(self) -> str:
        """Nombre identificador del check."""
        return "Security"

    @property
    def category(self) -> str:
        """Categoría del check."""
        return "security"

    @property
    def estimated_duration(self) -> float:
        """Duración estimada en segundos."""
        return 1.5

    @property
    def priority(self) -> int:
        """Prioridad de ejecución (1=más alta, 10=más baja)."""
        return 1  # Máxima prioridad - seguridad crítica

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
        if context.config and not context.config.check_security:
            return False

        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        """
        Ejecuta bandit sobre el archivo.

        Args:
            file_path: Ruta al archivo Python

        Returns:
            Lista de resultados de verificación
        """
        results = []

        try:
            # Ejecutar bandit con formato JSON para parsear fácilmente
            process = subprocess.run(
                ["bandit", "-f", "json", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Parsear output JSON
            try:
                data = json.loads(process.stdout)
                issues = data.get("results", [])

                if not issues:
                    # Sin problemas de seguridad
                    results.append(
                        CheckResult(
                            check_name=self.name,
                            severity=Severity.INFO,
                            message="✓ No security issues detected",
                            file_path=str(file_path),
                        )
                    )
                else:
                    # Procesar cada issue
                    for issue in issues:
                        severity = self._map_severity(issue.get("issue_severity", "LOW"))
                        issue_text = issue.get("issue_text", "Security issue")
                        line_number = issue.get("line_number")
                        test_id = issue.get("test_id", "")

                        # Crear mensaje descriptivo
                        message = f"Security: {issue_text}"
                        if test_id:
                            message = f"Security [{test_id}]: {issue_text}"

                        results.append(
                            CheckResult(
                                check_name=self.name,
                                severity=severity,
                                message=message,
                                file_path=str(file_path),
                                line_number=line_number,
                            )
                        )

            except json.JSONDecodeError:
                # Error parseando JSON
                results.append(
                    CheckResult(
                        check_name=self.name,
                        severity=Severity.ERROR,
                        message="Could not parse bandit JSON output",
                        file_path=str(file_path),
                    )
                )

        except FileNotFoundError:
            # bandit no instalado
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="bandit not installed. Run: pip install bandit",
                    file_path=str(file_path),
                )
            )
        except subprocess.TimeoutExpired:
            # Timeout
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="bandit execution timed out (>10s)",
                    file_path=str(file_path),
                )
            )
        except Exception as e:
            # Error inesperado
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message=f"Unexpected error running bandit: {str(e)}",
                    file_path=str(file_path),
                )
            )

        return results

    def _map_severity(self, bandit_severity: str) -> Severity:
        """
        Mapea severidad de bandit a Severity de CodeGuard.

        Args:
            bandit_severity: Severidad de bandit (HIGH, MEDIUM, LOW)

        Returns:
            Severidad correspondiente de CodeGuard
        """
        mapping = {
            "HIGH": Severity.ERROR,  # Crítico, debe corregirse
            "MEDIUM": Severity.WARNING,  # Importante, revisar
            "LOW": Severity.INFO,  # Informativo
        }
        return mapping.get(bandit_severity.upper(), Severity.INFO)
