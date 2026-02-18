"""
Check de imports sin uso con pylint.

Este check detecta imports que están declarados pero nunca usados,
ayudando a mantener el código limpio y las dependencias claras.

Fecha de creación: 2026-02-03
Ticket: 2.6
"""

import re
import subprocess
from pathlib import Path
from typing import List

from quality_agents.codeguard.agent import CheckResult, Severity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable


class ImportCheck(Verifiable):
    """
    Detecta imports sin uso usando pylint.

    Imports sin uso son problemáticos porque:
    - Aumentan el tiempo de carga del módulo
    - Confunden sobre las dependencias reales
    - Pueden ocultar errores de refactoring
    - Agregan ruido al código

    Este check usa pylint con configuración específica:
    - `--disable=all`: Desactiva todos los checks
    - `--enable=unused-import`: Solo detecta imports sin uso
    - Incluye el mensaje W0611

    Autofix disponible:
    El mensaje incluye sugerencia de usar autoflake para
    eliminar automáticamente los imports sin uso.

    Configuración:
        - check_imports: bool (habilitado por defecto)

    Prioridad: 6 (Baja - limpieza de código)
    Duración estimada: 0.5s
    """

    @property
    def name(self) -> str:
        """Nombre identificador del check."""
        return "UnusedImports"

    @property
    def category(self) -> str:
        """Categoría del check."""
        return "quality"

    @property
    def estimated_duration(self) -> float:
        """Duración estimada en segundos."""
        return 0.5

    @property
    def priority(self) -> int:
        """Prioridad de ejecución (1=más alta, 10=más baja)."""
        return 6

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
        if context.config and not context.config.check_imports:
            return False

        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        """
        Ejecuta pylint sobre el archivo para detectar imports sin uso.

        Args:
            file_path: Ruta al archivo Python

        Returns:
            Lista de resultados de verificación
        """
        results = []

        try:
            # Ejecutar pylint con solo el check de unused-import
            # --disable=all: desactiva todos los checks
            # --enable=unused-import: solo habilita W0611
            # --score=n: no mostrar score
            process = subprocess.run(
                [
                    "pylint",
                    "--disable=all",
                    "--enable=unused-import",
                    "--score=n",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            # Parsear output
            unused_imports = self._parse_pylint_output(process.stdout)

            if not unused_imports:
                # Sin imports sin uso
                results.append(
                    CheckResult(
                        check_name=self.name,
                        severity=Severity.INFO,
                        message="✓ No unused imports detected",
                        file_path=str(file_path),
                    )
                )
            else:
                # Reportar cada import sin uso
                for import_info in unused_imports:
                    message = (
                        f"Unused import: '{import_info['module']}'. "
                        f"Consider removing or use 'autoflake --remove-all-unused-imports' to auto-fix"
                    )

                    results.append(
                        CheckResult(
                            check_name=self.name,
                            severity=Severity.WARNING,
                            message=message,
                            file_path=str(file_path),
                            line_number=import_info["line"],
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
                    message="pylint execution timed out (>5s)",
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

    def _parse_pylint_output(self, output: str) -> List[dict]:
        """
        Parsea el output de pylint para extraer imports sin uso.

        Formato esperado:
            file.py:10:0: W0611: Unused import os (unused-import)
            file.py:15:0: W0611: Unused sys imported from sys (unused-import)

        Args:
            output: Output de pylint

        Returns:
            Lista de diccionarios con info de imports sin uso
        """
        unused_imports = []

        # Regex para capturar líneas de unused-import
        # Formato: file.py:line:col: W0611: Unused ... (unused-import)
        # Captura todo después de "Unused " hasta " (unused-import)"
        pattern = r"^.+?:(\d+):\d+:\s*W0611:\s*Unused\s+(.+?)\s+\(unused-import\)"

        for line in output.split("\n"):
            match = re.match(pattern, line.strip())
            if match:
                line_num = int(match.group(1))
                module_info = match.group(2).strip()

                # Limpiar el nombre del módulo
                # "import os" -> "os"
                # "sys imported from sys" -> "sys"
                if " imported from " in module_info:
                    module_name = module_info.split(" imported from ")[0]
                else:
                    module_name = module_info.replace("import ", "")

                unused_imports.append(
                    {
                        "line": line_num,
                        "module": module_name,
                    }
                )

        return unused_imports
