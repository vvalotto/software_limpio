"""
CouplingAnalyzer — Acoplamiento Aferente (Ca) y Eferente (Ce) por módulo.

Ca (Afferent Coupling): cuántos módulos internos dependen de este módulo.
Un Ca alto indica que el módulo es muy usado → alta responsabilidad.

Ce (Efferent Coupling): cuántos módulos internos importa este módulo.
Un Ce alto indica que el módulo depende de muchos otros → potencialmente frágil.

Ca y Ce son métricas informativas (sin umbral configurable). Su valor
principal es derivar I (Instability) y D (Distance from Main Sequence).
Los resultados son siempre INFO.

Ticket: 2.2
Fecha: 2026-03-01
"""

from pathlib import Path
from typing import Any, List

from quality_agents.architectanalyst.metrics.dependency_graph import DependencyGraphBuilder
from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity
from quality_agents.architectanalyst.orchestrator import ProjectMetric


class CouplingAnalyzer(ProjectMetric):
    """
    Reporta Ca (Afferent Coupling) y Ce (Efferent Coupling) por módulo.

    Emite un resultado INFO por cada módulo con al menos una dependencia
    (Ca > 0 o Ce > 0). Los módulos completamente aislados se omiten.

    Ca y Ce son métricas sin umbral — no generan WARNING ni CRITICAL.
    Su propósito es proveer contexto para InstabilityAnalyzer y DistanceAnalyzer.
    """

    @property
    def name(self) -> str:
        return "CouplingAnalyzer"

    @property
    def category(self) -> str:
        return "martin"

    @property
    def estimated_duration(self) -> float:
        return 3.0

    @property
    def priority(self) -> int:
        return 5

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        """
        Analiza el proyecto y retorna Ca/Ce por módulo.

        Args:
            project_path: Directorio raíz del proyecto.
            files: Lista de archivos Python a analizar.

        Returns:
            Lista de ArchitectureResult (INFO) con Ca y Ce para cada módulo
            que tiene al menos una dependencia entrante o saliente.
        """
        builder = DependencyGraphBuilder()
        graph = builder.build(project_path, files)

        results: List[ArchitectureResult] = []

        for module in sorted(graph.modules):
            ca = len(graph.afferent_coupling(module))
            ce = len(graph.efferent_coupling(module))

            # Módulos completamente aislados (sin deps ni dependientes) no aportan info
            if ca == 0 and ce == 0:
                continue

            results.append(ArchitectureResult(
                analyzer_name=self.name,
                metric_name="Coupling",
                module_path=Path(module.replace(".", "/")),
                value=float(ce),
                threshold=None,
                severity=ArchitectureSeverity.INFO,
                message=f"Ca={ca}, Ce={ce} — {'muy usado' if ca > ce else 'muchas deps' if ce > ca else 'balanceado'}",
            ))

        return results

    def should_run(self, config: Any) -> bool:
        return True
