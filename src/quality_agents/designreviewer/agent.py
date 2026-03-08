"""
DesignReviewer Agent - Implementación principal

Analiza la calidad de diseño del delta de un PR. A diferencia de CodeGuard,
puede bloquear el merge si detecta violaciones críticas.

Fecha de creación: 2026-02-19
Ticket: 1.3 - Refactorizar DesignReviewer como clase principal
"""

from pathlib import Path
from typing import List, Optional

from quality_agents.designreviewer.config import DesignReviewerConfig, load_config
from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity
from quality_agents.designreviewer.orchestrator import AnalyzerOrchestrator

# Re-exportar para compatibilidad con imports externos
__all__ = ["DesignReviewer", "ReviewResult", "ReviewSeverity"]


class DesignReviewer:
    """
    Agente de review para análisis profundo de calidad de diseño.

    Características:
        - Ejecuta en 2-5 minutos (modo PR review)
        - Puede bloquear el merge si hay violaciones CRITICAL
        - Analiza el delta del PR: solo archivos modificados + dependencias directas
        - Métricas: CBO, Fan-Out, Circular Imports, DIT, NOP, LCOM, WMC, Code Smells
        - Delega en AnalyzerOrchestrator para auto-discovery y ejecución de analyzers

    Attributes:
        path: Directorio raíz del proyecto a analizar.
        config_path: Ruta al archivo de configuración (opcional).
        results: Lista de resultados del último análisis ejecutado.
    """

    def __init__(
        self,
        path: Path = Path("."),
        config_path: Optional[Path] = None,
    ) -> None:
        """
        Inicializa DesignReviewer.

        Args:
            path: Directorio raíz del proyecto.
            config_path: Ruta al archivo de configuración (pyproject.toml o YAML).
        """
        self.path = path
        self.config_path = config_path
        self.results: List[ReviewResult] = []

        self._config: DesignReviewerConfig = load_config(
            config_path=config_path,
            project_root=path if path.is_dir() else path.parent,
        )
        self._orchestrator: AnalyzerOrchestrator = AnalyzerOrchestrator(self._config)

    def run(self, files: Optional[List[Path]] = None) -> List[ReviewResult]:
        """
        Ejecuta análisis sobre los archivos especificados.

        Delega en AnalyzerOrchestrator para seleccionar y ejecutar los analyzers
        apropiados según el contexto.

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

        return self.results

    def analyze_delta(self, changed_files: List[Path]) -> List[ReviewResult]:
        """
        Analiza solo los archivos modificados en el PR (delta).

        Es el modo principal de uso: recibe la lista de archivos cambiados
        en el PR y analiza su calidad de diseño.

        Args:
            changed_files: Lista de archivos modificados en el PR.

        Returns:
            Lista de resultados del análisis.
        """
        return self.run(files=changed_files)

    def should_block(self) -> bool:
        """
        Determina si el merge debe ser bloqueado.

        Returns:
            True si hay al menos un resultado con severidad CRITICAL.
        """
        return any(r.is_blocking() for r in self.results)

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


# --- CLI --- (imports aquí para evitar importación circular con formatter.py)

import os  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import click  # noqa: E402

from quality_agents.designreviewer.formatter import format_json, format_results  # noqa: E402


def _common_parent(paths: List[Path]) -> Path:
    """Calcula el directorio padre común de una lista de paths."""
    if len(paths) == 1:
        return paths[0] if paths[0].is_dir() else paths[0].parent
    resolved = [p.resolve() for p in paths]
    common = Path(os.path.commonpath([str(p) for p in resolved]))
    return common if common.is_dir() else common.parent


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    help="Archivo de configuración (pyproject.toml o YAML)",
)
@click.option(
    "--format", "-f",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Formato de salida",
)
@click.option(
    "--no-ai",
    is_flag=True,
    default=False,
    help="Deshabilitar sugerencias de IA",
)
def main(paths: tuple, config: Optional[str], output_format: str, no_ai: bool) -> None:
    """
    DesignReviewer - Análisis de calidad de diseño sobre el delta de un PR.

    Analiza archivos Python en los PATHS indicados (archivos o directorios).
    Acepta uno o más paths. Sin argumentos analiza el directorio actual.

    Ejemplos:
      designreviewer src/
      designreviewer entidades servicios

    Bloquea (exit code 1) si detecta violaciones CRITICAL.
    """
    targets = [Path(p) for p in paths] if paths else [Path(".")]
    config_path = Path(config) if config else None

    project_root = _common_parent(targets)
    reviewer = DesignReviewer(path=project_root, config_path=config_path)

    all_files: List[Path] = []
    for target in targets:
        all_files.extend(reviewer.collect_files(target))

    start = time.time()
    results = reviewer.run(files=all_files)
    elapsed = time.time() - start

    total_files = len(all_files)
    analyzers_executed = len(reviewer._orchestrator.analyzers)

    if output_format == "json":
        click.echo(format_json(results, elapsed, total_files, analyzers_executed))
    else:
        format_results(results, elapsed, total_files, analyzers_executed)

    if any(r.is_blocking() for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
