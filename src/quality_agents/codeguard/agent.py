"""
CodeGuard Agent - Implementación principal

Fecha de actualización: 2026-02-03
Ticket: 2.5.1 - Integración con orquestador
Ticket: 4.3 - Integración con formatter Rich
"""

import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

from quality_agents.codeguard.config import CodeGuardConfig, load_config
from quality_agents.codeguard.orchestrator import CheckOrchestrator
from quality_agents.shared.verifiable import ExecutionContext


class Severity(Enum):
    """Niveles de severidad para los resultados de verificación."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class CheckResult:
    """Resultado de una verificación individual."""
    check_name: str
    severity: Severity
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None


class CodeGuard:
    """
    Agente de pre-commit para verificaciones rápidas de calidad.

    Características:
        - Ejecuta en < 5 segundos (modo pre-commit)
        - Solo advierte, nunca bloquea commits
        - Verifica: PEP8, Pylint score, imports, seguridad, tipos, complejidad
        - Usa orquestador para selección contextual de checks

    Attributes:
        config: Configuración cargada desde pyproject.toml o YAML
        orchestrator: Orquestador que selecciona checks según contexto
        results: Lista de resultados de verificación
    """

    def __init__(self, config_path: Optional[Path] = None, project_root: Optional[Path] = None):
        """
        Inicializa CodeGuard.

        Args:
            config_path: Ruta al archivo de configuración (opcional)
            project_root: Raíz del proyecto (para buscar config automáticamente)
        """
        self.config_path = config_path
        self.project_root = project_root or Path.cwd()

        # Cargar configuración
        self.config = load_config(config_path, self.project_root)

        # Inicializar orquestador
        self.orchestrator = CheckOrchestrator(self.config)

        self.results: List[CheckResult] = []

    def run(
        self,
        files: List[Path],
        analysis_type: str = "pre-commit",
        time_budget: Optional[float] = None,
    ) -> List[CheckResult]:
        """
        Ejecuta verificaciones sobre los archivos especificados.

        Usa el orquestador para seleccionar checks según el contexto.
        El orquestador decide qué checks ejecutar basándose en:
        - Tipo de análisis (pre-commit, pr-review, full)
        - Presupuesto de tiempo
        - Prioridades de checks
        - Estado del archivo (nuevo, modificado, excluido)

        Args:
            files: Lista de archivos a verificar
            analysis_type: Tipo de análisis ("pre-commit", "pr-review", "full")
            time_budget: Presupuesto de tiempo en segundos (None = sin límite)

        Returns:
            Lista de resultados de verificación

        Example:
            >>> guard = CodeGuard()
            >>> files = [Path("app.py"), Path("utils.py")]
            >>> results = guard.run(files, analysis_type="pre-commit", time_budget=5.0)
            >>> # Ejecuta solo checks rápidos y críticos
        """
        self.results = []

        # Filtrar solo archivos Python
        python_files = [f for f in files if f.suffix == ".py"]

        for file_path in python_files:
            # Crear contexto de ejecución
            context = ExecutionContext(
                file_path=file_path,
                is_excluded=self._is_excluded(file_path),
                config=self.config,
                analysis_type=analysis_type,
                time_budget=time_budget,
                is_modified=True,  # Por ahora asumir modificado
                is_new_file=False,
                ai_enabled=self.config.ai.enabled if self.config.ai else False,
            )

            # Si el archivo está excluido, saltar
            if context.is_excluded:
                continue

            # Seleccionar checks según contexto
            selected_checks = self.orchestrator.select_checks(context)

            # Ejecutar cada check seleccionado
            for check in selected_checks:
                try:
                    check_results = check.execute(file_path)
                    self.results.extend(check_results)
                except Exception as e:
                    # Si un check falla, registrar error pero continuar
                    self.results.append(
                        CheckResult(
                            check_name=check.name,
                            severity=Severity.ERROR,
                            message=f"Check failed with error: {str(e)}",
                            file_path=str(file_path),
                        )
                    )

        return self.results

    def _is_excluded(self, file_path: Path) -> bool:
        """
        Verifica si un archivo debe ser excluido del análisis.

        Args:
            file_path: Ruta al archivo

        Returns:
            True si el archivo debe ser excluido, False en caso contrario
        """
        # Verificar patrones de exclusión de la configuración
        for pattern in self.config.exclude_patterns:
            if pattern in str(file_path):
                return True

        return False

    def collect_files(self, path: Path) -> List[Path]:
        """
        Recolecta archivos Python a analizar.

        Args:
            path: Directorio o archivo a analizar

        Returns:
            Lista de archivos Python
        """
        if path.is_file():
            return [path] if path.suffix == ".py" else []

        return list(path.rglob("*.py"))


# --- CLI ---

import click

from quality_agents.codeguard.formatter import format_results, format_json


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    help="Archivo de configuración (pyproject.toml o YAML)"
)
@click.option(
    "--format", "-f",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Formato de salida"
)
@click.option(
    "--analysis-type", "-a",
    type=click.Choice(["pre-commit", "pr-review", "full"]),
    default="pre-commit",
    help="Tipo de análisis (determina qué checks ejecutar)"
)
@click.option(
    "--time-budget", "-t",
    type=float,
    default=None,
    help="Presupuesto de tiempo en segundos (None = sin límite)"
)
def main(
    path: str,
    config: Optional[str],
    format: str,
    analysis_type: str,
    time_budget: Optional[float],
) -> None:
    """
    CodeGuard - Verificación de calidad de código con orquestación inteligente.

    Analiza archivos Python en PATH (archivo o directorio).

    Tipos de análisis:
    - pre-commit: Checks rápidos y críticos (<5s)
    - pr-review: Todos los checks habilitados
    - full: Análisis completo sin restricciones
    """
    target = Path(path)
    config_path = Path(config) if config else None

    guard = CodeGuard(config_path=config_path, project_root=target if target.is_dir() else target.parent)
    files = guard.collect_files(target)

    # Solo mostrar información si formato es texto
    # (en JSON solo queremos el JSON puro para facilitar parsing)
    if format == "text":
        click.echo(f"CodeGuard v0.2.0 (Arquitectura Modular)")
        click.echo(f"Analizando: {target.absolute()}")
        click.echo(f"Archivos Python encontrados: {len(files)}")
        click.echo(f"Tipo de análisis: {analysis_type}")

        if time_budget:
            click.echo(f"Presupuesto de tiempo: {time_budget}s")

        if config_path:
            click.echo(f"Configuración: {config_path}")

        click.echo(f"\nChecks disponibles: {len(guard.orchestrator.checks)}")
        click.echo("---")

    # Ejecutar checks con orquestador (medir tiempo)
    start_time = time.time()
    results = guard.run(files, analysis_type=analysis_type, time_budget=time_budget)
    elapsed = time.time() - start_time

    # Mostrar resultados con formatters nuevos
    if format == "text":
        # Usar Rich formatter
        format_results(
            results,
            elapsed=elapsed,
            total_files=len(files),
            checks_executed=len(guard.orchestrator.checks),
        )
    else:
        # Usar JSON formatter
        json_output = format_json(
            results,
            elapsed=elapsed,
            total_files=len(files),
            checks_executed=len(guard.orchestrator.checks),
        )
        click.echo(json_output)


if __name__ == "__main__":
    main()
