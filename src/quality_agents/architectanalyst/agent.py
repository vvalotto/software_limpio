"""
ArchitectAnalyst Agent - Implementación principal

Analiza la salud arquitectónica del sistema completo al finalizar un sprint.
A diferencia de CodeGuard y DesignReviewer, nunca bloquea — es informativo y estratégico.

Fecha de creación: 2026-02-28
Ticket: 1.2 - Refactorizar ArchitectAnalyst como clase principal
"""

from pathlib import Path
from typing import List, Optional

from quality_agents.architectanalyst.config import ArchitectAnalystConfig, load_config
from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity
from quality_agents.architectanalyst.orchestrator import MetricOrchestrator
from quality_agents.architectanalyst.snapshots import SnapshotStore
from quality_agents.architectanalyst.trends import TrendCalculator

# Re-exportar para compatibilidad con imports externos
__all__ = ["ArchitectAnalyst", "ArchitectureResult", "ArchitectureSeverity"]


class ArchitectAnalyst:
    """
    Agente de análisis arquitectónico para fin de sprint.

    Características:
        - Ejecuta manualmente al finalizar un sprint o milestone
        - Analiza el sistema completo (no solo el delta del PR)
        - Métricas: Ca, Ce, I, A, D (Métricas de Martin) + ciclos + violaciones de capas
        - Nunca bloquea (exit code siempre 0) — es informativo y estratégico
        - Delega en MetricOrchestrator para auto-discovery y ejecución de analyzers
        - Persiste snapshots en SQLite para comparación de tendencias entre sprints

    Attributes:
        path: Directorio raíz del proyecto a analizar.
        config_path: Ruta al archivo de configuración (opcional).
        sprint_id: Identificador del sprint actual (opcional, para histórico).
        results: Lista de resultados del último análisis ejecutado.
    """

    def __init__(
        self,
        path: Path = Path("."),
        config_path: Optional[Path] = None,
        sprint_id: Optional[str] = None,
    ) -> None:
        """
        Inicializa ArchitectAnalyst.

        Args:
            path: Directorio raíz del proyecto.
            config_path: Ruta al archivo de configuración (pyproject.toml o YAML).
            sprint_id: Identificador del sprint (ej: "sprint-12", "2026-Q1").
        """
        self.path = path
        self.config_path = config_path
        self.sprint_id = sprint_id
        self.results: List[ArchitectureResult] = []

        self._config: ArchitectAnalystConfig = load_config(
            config_path=config_path,
            project_root=path if path.is_dir() else path.parent,
        )
        self._orchestrator: MetricOrchestrator = MetricOrchestrator(self._config)

        project_root = path if path.is_dir() else path.parent
        db_path = project_root / self._config.db_path
        self._store: SnapshotStore = SnapshotStore(db_path)
        self._trend_calculator: TrendCalculator = TrendCalculator()

    def run(self, files: Optional[List[Path]] = None) -> List[ArchitectureResult]:
        """
        Ejecuta análisis arquitectónico sobre el proyecto.

        Delega en MetricOrchestrator para seleccionar y ejecutar los analyzers.

        Args:
            files: Archivos a analizar. Si es None, analiza todos los Python en self.path.

        Returns:
            Lista de resultados del análisis.
        """
        self.results = []

        if files is None:
            files = self.collect_files(self.path)

        python_files = [f for f in files if f.suffix == ".py"]

        if self._orchestrator is not None:
            self.results = self._orchestrator.run(python_files)

        # Enriquecer con tendencias si hay snapshot anterior
        previous = self._store.get_latest_results()
        if previous:
            self.results = self._trend_calculator.enrich(self.results, previous)

        # Persistir snapshot actual
        self._store.save(
            self.results,
            sprint_id=self.sprint_id,
            project_path=str(self.path),
        )

        return self.results

    def collect_files(self, path: Path) -> List[Path]:
        """
        Recolecta archivos Python a analizar, respetando exclude_patterns de la config.

        Args:
            path: Directorio o archivo a analizar.

        Returns:
            Lista de archivos Python encontrados, excluyendo los patrones configurados.
        """
        if path.is_file():
            return [path] if path.suffix == ".py" else []
        exclude = self._config.exclude_patterns
        if exclude:
            return [
                f for f in path.rglob("*.py")
                if not any(pattern in str(f.relative_to(path)) for pattern in exclude)
            ]
        return list(path.rglob("*.py"))

    def has_violations(self) -> bool:
        """Retorna True si hay alguna violación (WARNING o CRITICAL)."""
        return any(r.has_violation() for r in self.results)

    def has_critical(self) -> bool:
        """Retorna True si hay alguna violación CRITICAL."""
        return any(r.is_critical() for r in self.results)


# --- CLI --- (imports aquí para evitar importación circular con formatter.py)

import time  # noqa: E402

import click  # noqa: E402

from quality_agents.architectanalyst.formatter import format_json, format_results  # noqa: E402


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    help="Archivo de configuración (pyproject.toml)",
)
@click.option(
    "--format", "-f",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Formato de salida (default: text)",
)
@click.option(
    "--sprint-id", "-s",
    default=None,
    help="Identificador del sprint (ej: sprint-12, 2026-Q1)",
)
def main(path: str, config: Optional[str], output_format: str, sprint_id: Optional[str]) -> None:
    """
    ArchitectAnalyst - Análisis arquitectónico de fin de sprint.

    Analiza el proyecto en PATH (directorio). Calcula métricas de Martin (Ca, Ce, I, A, D),
    detecta ciclos de dependencias y violaciones de capas. Persiste snapshot para
    comparar tendencias entre sprints.

    Nunca bloquea — exit code siempre 0.
    """
    target = Path(path)
    config_path = Path(config) if config else None

    analyst = ArchitectAnalyst(path=target, config_path=config_path, sprint_id=sprint_id)

    start = time.time()
    results = analyst.run()
    elapsed = time.time() - start

    files = analyst.collect_files(target)
    total_files = len([f for f in files if f.suffix == ".py"])
    metrics_executed = len(analyst._orchestrator.metrics)

    if output_format == "json":
        click.echo(format_json(results, elapsed, total_files, metrics_executed, sprint_id))
    else:
        format_results(results, elapsed, total_files, metrics_executed, sprint_id)

    # Exit code siempre 0 — ArchitectAnalyst es informativo, nunca bloquea


if __name__ == "__main__":
    main()
