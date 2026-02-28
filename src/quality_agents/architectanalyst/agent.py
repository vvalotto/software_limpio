"""
ArchitectAnalyst Agent - Implementación principal

Analiza la salud arquitectónica del sistema completo al finalizar un sprint.
A diferencia de CodeGuard y DesignReviewer, nunca bloquea — es informativo y estratégico.

Fecha de creación: 2026-02-28
Ticket: 1.2 - Refactorizar ArchitectAnalyst como clase principal
"""

from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity

if TYPE_CHECKING:
    from quality_agents.architectanalyst.config import ArchitectAnalystConfig
    from quality_agents.architectanalyst.orchestrator import MetricOrchestrator

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

        # Wired en ticket 1.4 (config) y 1.3 (orchestrator)
        self._config: Optional["ArchitectAnalystConfig"] = None
        self._orchestrator: Optional["MetricOrchestrator"] = None

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

        return self.results

    def collect_files(self, path: Path) -> List[Path]:
        """
        Recolecta archivos Python a analizar.

        Args:
            path: Directorio o archivo a analizar.

        Returns:
            Lista de archivos Python encontrados.
        """
        if path.is_file():
            return [path] if path.suffix == ".py" else []
        return list(path.rglob("*.py"))

    def has_violations(self) -> bool:
        """Retorna True si hay alguna violación (WARNING o CRITICAL)."""
        return any(r.has_violation() for r in self.results)

    def has_critical(self) -> bool:
        """Retorna True si hay alguna violación CRITICAL."""
        return any(r.is_critical() for r in self.results)
