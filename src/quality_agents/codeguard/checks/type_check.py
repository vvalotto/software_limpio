"""
Check de tipos usando mypy.

Este check detecta errores de tipo en código Python con type hints,
ayudando a prevenir bugs relacionados con tipos incorrectos.

Fecha de creación: 2026-02-03
Ticket: 2.5
"""

import re
import subprocess
from pathlib import Path
from typing import List

from quality_agents.shared.verifiable import ExecutionContext, Verifiable
from quality_agents.codeguard.agent import CheckResult, Severity


class TypeCheck(Verifiable):
    """
    Detecta errores de tipo usando mypy.

    Type hints en Python mejoran:
    - Detección temprana de errores de tipo
    - Documentación del código (tipos esperados)
    - Autocompletado en IDEs
    - Refactoring más seguro

    Este check es INTELIGENTE:
    - Solo ejecuta mypy si el archivo tiene type hints
    - No penaliza código sin hints (es opcional)
    - Si hay hints, verifica que sean correctos

    Detección de type hints:
    - Busca anotaciones de parámetros: `def func(x: int)`
    - Busca anotaciones de retorno: `-> str`
    - Busca anotaciones de variables: `name: str = "test"`

    Configuración:
        - check_types: bool (habilitado por defecto)

    Prioridad: 5 (Media-baja - type hints son opcionales)
    Duración estimada: 3.0s (mypy puede ser lento)
    """

    @property
    def name(self) -> str:
        """Nombre identificador del check."""
        return "Types"

    @property
    def category(self) -> str:
        """Categoría del check."""
        return "quality"

    @property
    def estimated_duration(self) -> float:
        """Duración estimada en segundos."""
        return 3.0

    @property
    def priority(self) -> int:
        """Prioridad de ejecución (1=más alta, 10=más baja)."""
        return 5

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
        if context.config and not context.config.check_types:
            return False

        # Verificar si el archivo tiene type hints
        # (no ejecutar mypy en archivos sin hints)
        if not self._has_type_hints(context.file_path):
            return False

        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        """
        Ejecuta mypy sobre el archivo.

        Args:
            file_path: Ruta al archivo Python

        Returns:
            Lista de resultados de verificación
        """
        results = []

        try:
            # Ejecutar mypy
            # --no-error-summary: no mostrar resumen al final
            # --show-column-numbers: mostrar número de columna
            # --no-color-output: output sin colores ANSI
            process = subprocess.run(
                [
                    "mypy",
                    "--no-error-summary",
                    "--show-column-numbers",
                    "--no-color-output",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # mypy retorna exit code 0 si no hay errores
            # exit code 1 si hay errores de tipo
            if process.returncode == 0 and not process.stdout.strip():
                # Sin errores de tipo
                results.append(
                    CheckResult(
                        check_name=self.name,
                        severity=Severity.INFO,
                        message="✓ No type errors detected",
                        file_path=str(file_path),
                    )
                )
            else:
                # Parsear errores
                errors = self._parse_mypy_output(process.stdout)

                if not errors:
                    # No se encontraron errores parseables
                    # pero mypy reportó algo (puede ser warning)
                    results.append(
                        CheckResult(
                            check_name=self.name,
                            severity=Severity.INFO,
                            message="✓ Type checking completed",
                            file_path=str(file_path),
                        )
                    )
                else:
                    for error in errors:
                        results.append(
                            CheckResult(
                                check_name=self.name,
                                severity=Severity.WARNING,
                                message=f"Type: {error['message']}",
                                file_path=str(file_path),
                                line_number=error["line"],
                            )
                        )

        except FileNotFoundError:
            # mypy no instalado
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="mypy not installed. Run: pip install mypy",
                    file_path=str(file_path),
                )
            )
        except subprocess.TimeoutExpired:
            # Timeout
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="mypy execution timed out (>10s)",
                    file_path=str(file_path),
                )
            )
        except Exception as e:
            # Error inesperado
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message=f"Unexpected error running mypy: {str(e)}",
                    file_path=str(file_path),
                )
            )

        return results

    def _has_type_hints(self, file_path: Path) -> bool:
        """
        Detecta si el archivo tiene type hints.

        Busca patrones comunes:
        - def func(x: int) - parámetros con tipo
        - -> str - retorno con tipo
        - name: str = - variables con tipo

        Args:
            file_path: Ruta al archivo

        Returns:
            True si tiene type hints, False en caso contrario
        """
        try:
            content = file_path.read_text(encoding="utf-8")

            # Patrones de type hints
            patterns = [
                r":\s*\w+\s*[,\)]",  # parámetro: tipo,  o  parámetro: tipo)
                r"->\s*\w+",  # -> tipo
                r":\s*\w+\s*=",  # variable: tipo =
                r":\s*List\[",  # List[tipo]
                r":\s*Dict\[",  # Dict[tipo, tipo]
                r":\s*Optional\[",  # Optional[tipo]
                r":\s*Union\[",  # Union[tipo, tipo]
                r":\s*Tuple\[",  # Tuple[tipo, ...]
            ]

            for pattern in patterns:
                if re.search(pattern, content):
                    return True

            return False

        except Exception:
            # Si no se puede leer el archivo, asumir que no tiene hints
            return False

    def _parse_mypy_output(self, output: str) -> List[dict]:
        """
        Parsea el output de mypy.

        Formato esperado:
            file.py:10:5: error: Message here
            file.py:20:10: note: Additional info

        Args:
            output: Output de mypy

        Returns:
            Lista de diccionarios con info de errores
        """
        errors = []

        # Regex para capturar líneas de error
        # Formato: file.py:line:col: level: message
        # o: file.py:line: level: message (sin columna)
        # Capturamos el último número antes de : error: o : warning:
        pattern = r"^.+?:(\d+)(?::\d+)?:\s*(error|warning):\s*(.+)$"

        for line in output.split("\n"):
            match = re.match(pattern, line.strip())
            if match:
                line_num = int(match.group(1))
                level = match.group(2)
                message = match.group(3)

                # Solo reportar errors y warnings, ignorar notes
                if level in ("error", "warning"):
                    errors.append(
                        {
                            "line": line_num,
                            "level": level,
                            "message": message,
                        }
                    )

        return errors
