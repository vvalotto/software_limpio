"""
Check de complejidad ciclomática usando radon.

Este check detecta funciones y métodos con alta complejidad ciclomática,
que son difíciles de entender, mantener y probar.

Fecha de creación: 2026-02-03
Ticket: 2.4
"""

import re
import subprocess
from pathlib import Path
from typing import List

from quality_agents.codeguard.agent import CheckResult, Severity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable


class ComplexityCheck(Verifiable):
    """
    Detecta funciones con alta complejidad ciclomática usando radon.

    La complejidad ciclomática (CC) mide el número de caminos independientes
    a través del código. CC alto indica:
    - Código difícil de entender
    - Difícil de mantener
    - Difícil de probar (necesita muchos tests)
    - Mayor probabilidad de bugs

    Grades de radon:
        A: CC 1-5 (simple, fácil de mantener)
        B: CC 6-10 (moderado)
        C: CC 11-20 (complejo, refactorizar)
        D: CC 21-50 (muy complejo, alto riesgo)
        E: CC 51-100 (extremadamente complejo)
        F: CC >100 (no mantenible)

    Configuración:
        - check_complexity: bool (habilitado por defecto)
        - max_cyclomatic_complexity: int (default: 10)

    Prioridad: 3 (Alta - calidad importante)
    Duración estimada: 1.0s
    """

    @property
    def name(self) -> str:
        """Nombre identificador del check."""
        return "Complexity"

    @property
    def category(self) -> str:
        """Categoría del check."""
        return "complexity"

    @property
    def estimated_duration(self) -> float:
        """Duración estimada en segundos."""
        return 1.0

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
        if context.config and not context.config.check_complexity:
            return False

        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        """
        Ejecuta radon sobre el archivo.

        Args:
            file_path: Ruta al archivo Python

        Returns:
            Lista de resultados de verificación
        """
        results = []

        try:
            # Ejecutar radon cc con formato show_complexity (-s)
            # -s muestra el score de complejidad
            process = subprocess.run(
                ["radon", "cc", "-s", str(file_path)],
                capture_output=True,
                text=True,
                timeout=5,
            )

            # Parsear output
            # Formato: <tipo> <linea>:<col> <nombre> - <grade> (<CC>)
            # Ejemplo: F 10:0 complex_function - C (11)
            functions = self._parse_radon_output(process.stdout)

            if not functions:
                # Sin funciones complejas
                results.append(
                    CheckResult(
                        check_name=self.name,
                        severity=Severity.INFO,
                        message="✓ No complex functions detected",
                        file_path=str(file_path),
                    )
                )
            else:
                # Obtener max_cc de config (default: 10)
                max_cc = 10
                if hasattr(self, "_context") and self._context.config:
                    max_cc = self._context.config.max_cyclomatic_complexity

                # Procesar cada función con CC > max_cc
                complex_functions = [f for f in functions if f["complexity"] > max_cc]

                if not complex_functions:
                    results.append(
                        CheckResult(
                            check_name=self.name,
                            severity=Severity.INFO,
                            message=f"✓ All functions below complexity threshold (≤{max_cc})",
                            file_path=str(file_path),
                        )
                    )
                else:
                    for func in complex_functions:
                        severity = self._map_severity(func["complexity"], max_cc)
                        message = (
                            f"Complexity: {func['name']} has cyclomatic complexity "
                            f"{func['complexity']} (grade {func['grade']}). "
                            f"Consider refactoring into smaller functions."
                        )

                        results.append(
                            CheckResult(
                                check_name=self.name,
                                severity=severity,
                                message=message,
                                file_path=str(file_path),
                                line_number=func["line"],
                            )
                        )

        except FileNotFoundError:
            # radon no instalado
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="radon not installed. Run: pip install radon",
                    file_path=str(file_path),
                )
            )
        except subprocess.TimeoutExpired:
            # Timeout
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="radon execution timed out (>5s)",
                    file_path=str(file_path),
                )
            )
        except Exception as e:
            # Error inesperado
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message=f"Unexpected error running radon: {str(e)}",
                    file_path=str(file_path),
                )
            )

        return results

    def _parse_radon_output(self, output: str) -> List[dict]:
        """
        Parsea el output de radon cc -s.

        Formato esperado:
            file.py
                F 10:0 function_name - C (11)
                M 20:4 Class.method - B (8)

        Args:
            output: Output de radon

        Returns:
            Lista de diccionarios con info de funciones
        """
        functions = []

        # Regex para capturar líneas de funciones/métodos
        # Formato: <tipo> <linea>:<col> <nombre> - <grade> (<CC>)
        pattern = r"^\s*[FMC]\s+(\d+):\d+\s+(.+?)\s+-\s+([A-F])\s+\((\d+)\)"

        for line in output.split("\n"):
            match = re.match(pattern, line)
            if match:
                line_num = int(match.group(1))
                name = match.group(2)
                grade = match.group(3)
                complexity = int(match.group(4))

                functions.append(
                    {
                        "line": line_num,
                        "name": name,
                        "grade": grade,
                        "complexity": complexity,
                    }
                )

        return functions

    def _map_severity(self, complexity: int, max_cc: int) -> Severity:
        """
        Mapea complejidad a severidad.

        Args:
            complexity: Complejidad ciclomática
            max_cc: Umbral máximo configurado

        Returns:
            Severidad correspondiente
        """
        # Si está dentro del umbral, INFO
        if complexity <= max_cc:
            return Severity.INFO

        # Si excede pero no es crítico (hasta 20), WARNING
        if complexity <= 20:
            return Severity.WARNING

        # Si es muy alto (>20), ERROR
        return Severity.ERROR
