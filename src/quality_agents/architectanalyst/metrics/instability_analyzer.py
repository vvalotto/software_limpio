"""
InstabilityAnalyzer — Inestabilidad (I) por módulo.

I (Instability) = Ce / (Ca + Ce)

Rango: [0.0, 1.0]
  0.0 = totalmente estable — muchos dependen de él, él no depende de nadie
  1.0 = totalmente inestable — nadie depende de él, él depende de muchos

Un módulo con I alto es frágil porque cambios en sus dependencias lo afectan
sin que otros módulos absorban el impacto. Idealmente los módulos estables
(I bajo) son abstracciones (A alto), y los inestables son implementaciones (A bajo).

Umbral: max_instability en ArchitectAnalystConfig (default: 0.8).
Severidad: WARNING si I > max_instability.

Ticket: 2.3
Fecha: 2026-03-01
"""

from pathlib import Path
from typing import Any, List

from quality_agents.architectanalyst.metrics._utils import calculate_instability
from quality_agents.architectanalyst.metrics.dependency_graph import DependencyGraphBuilder
from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity
from quality_agents.architectanalyst.orchestrator import ProjectMetric


class InstabilityAnalyzer(ProjectMetric):
    """
    Detecta módulos con inestabilidad excesiva (I > max_instability).

    I = Ce / (Ca + Ce)

    Solo genera resultados cuando I supera el umbral configurado (WARNING).
    Los módulos aislados (Ca=0, Ce=0) tienen I=0.0 por definición y se omiten.

    Umbral por defecto: 0.8 (configurable vía max_instability en pyproject.toml).
    Severidad: WARNING.
    """

    @property
    def name(self) -> str:
        return "InstabilityAnalyzer"

    @property
    def category(self) -> str:
        return "martin"

    @property
    def estimated_duration(self) -> float:
        return 3.0

    @property
    def priority(self) -> int:
        return 6

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        """
        Analiza el proyecto y reporta módulos con inestabilidad excesiva.

        Args:
            project_path: Directorio raíz del proyecto.
            files: Lista de archivos Python a analizar.

        Returns:
            Lista de ArchitectureResult WARNING para módulos con I > max_instability.
        """
        config = self._config
        threshold = config.max_instability if config is not None else 0.8

        builder = DependencyGraphBuilder()
        graph = builder.build(project_path, files)

        results: List[ArchitectureResult] = []

        for module in sorted(graph.modules):
            ca = len(graph.afferent_coupling(module))
            ce = len(graph.efferent_coupling(module))

            # Módulos aislados: I=0.0 por convención (no violan nada)
            if ca == 0 and ce == 0:
                continue

            instability = calculate_instability(ca, ce)

            if instability > threshold:
                results.append(ArchitectureResult(
                    analyzer_name=self.name,
                    metric_name="I",
                    module_path=Path(module.replace(".", "/")),
                    value=round(instability, 3),
                    threshold=threshold,
                    severity=ArchitectureSeverity.WARNING,
                    message=(
                        f"Inestabilidad I={instability:.2f} > {threshold} "
                        f"(Ca={ca}, Ce={ce}). Módulo depende de muchos otros "
                        f"sin que nadie estabilice sus dependencias."
                    ),
                ))

        return results

    def __init__(self) -> None:
        self._config: Any = None

    def should_run(self, config: Any) -> bool:
        self._config = config
        return True
