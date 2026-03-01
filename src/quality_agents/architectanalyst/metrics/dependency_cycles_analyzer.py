"""
DependencyCyclesAnalyzer — Ciclos de dependencias entre módulos.

Detecta cualquier ciclo en el grafo de imports del proyecto usando el
algoritmo de Tarjan para encontrar Strongly Connected Components (SCCs).
Cada SCC con ≥ 2 nodos es un ciclo de dependencias.

Los ciclos violan el Principio de Dependencias Acíclicas (ADP) de Robert C. Martin.
Son siempre CRITICAL — no hay umbral configurable: cero ciclos es el único valor aceptable.

Ticket: 3.1
Fecha: 2026-03-01
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Set

from quality_agents.architectanalyst.metrics.dependency_graph import (
    DependencyGraph,
    DependencyGraphBuilder,
)
from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity
from quality_agents.architectanalyst.orchestrator import ProjectMetric

logger = logging.getLogger(__name__)


class DependencyCyclesAnalyzer(ProjectMetric):
    """
    Detecta ciclos de dependencias entre módulos del proyecto.

    Usa el algoritmo de Tarjan para encontrar SCCs (Strongly Connected Components)
    con más de un nodo. Cada SCC con size ≥ 2 representa un ciclo de dependencias.

    A diferencia de CircularImportsAnalyzer de DesignReviewer (que solo detecta
    ciclos directos A↔B), este analyzer detecta ciclos de cualquier longitud:
    A→B→C→A, A→B→C→D→A, etc.

    Severidad: siempre CRITICAL. threshold=0 (no configurable).
    priority=1 — máxima prioridad, los ciclos bloquean la comprensión del sistema.
    """

    @property
    def name(self) -> str:
        return "DependencyCyclesAnalyzer"

    @property
    def category(self) -> str:
        return "cycles"

    @property
    def estimated_duration(self) -> float:
        return 5.0

    @property
    def priority(self) -> int:
        return 1

    def should_run(self, config: Any) -> bool:
        return True

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        """
        Analiza el proyecto y reporta cada ciclo de dependencias detectado.

        Args:
            project_path: Directorio raíz del proyecto.
            files: Lista de archivos Python a analizar.

        Returns:
            Lista de ArchitectureResult CRITICAL, uno por ciclo detectado.
        """
        builder = DependencyGraphBuilder()
        graph = builder.build(project_path, files)

        cycles = self._find_cycles_tarjan(graph)

        results: List[ArchitectureResult] = []

        for cycle in cycles:
            # Normalizar: rotar el ciclo para que empiece con el módulo menor
            min_idx = cycle.index(min(cycle))
            normalized = cycle[min_idx:] + cycle[:min_idx]
            representative = normalized[0]

            cycle_str = " → ".join(normalized + [normalized[0]])

            results.append(ArchitectureResult(
                analyzer_name=self.name,
                metric_name="DependencyCycle",
                module_path=Path(representative.replace(".", "/")),
                value=float(len(cycle)),
                threshold=0.0,
                severity=ArchitectureSeverity.CRITICAL,
                message=(
                    f"Ciclo de dependencias con {len(cycle)} módulos: {cycle_str}. "
                    "Viola el Principio de Dependencias Acíclicas (ADP)."
                ),
            ))

        return results

    # -------------------------------------------------------------------------
    # Algoritmo de Tarjan para SCCs
    # -------------------------------------------------------------------------

    def _find_cycles_tarjan(self, graph: DependencyGraph) -> List[List[str]]:
        """
        Encuentra SCCs con ≥ 2 nodos usando el algoritmo de Tarjan.

        Cada SCC con más de un nodo es un ciclo de dependencias real.

        Returns:
            Lista de ciclos, cada uno como lista de nombres de módulos.
        """
        modules = sorted(graph.modules)
        index_counter = [0]
        index: Dict[str, int] = {}
        lowlink: Dict[str, int] = {}
        on_stack: Set[str] = set()
        stack: List[str] = []
        sccs: List[List[str]] = []

        def strongconnect(v: str) -> None:
            index[v] = lowlink[v] = index_counter[0]
            index_counter[0] += 1
            stack.append(v)
            on_stack.add(v)

            for w in sorted(graph.efferent_coupling(v)):
                if w not in index:
                    strongconnect(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                elif w in on_stack:
                    lowlink[v] = min(lowlink[v], index[w])

            if lowlink[v] == index[v]:
                scc: List[str] = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    scc.append(w)
                    if w == v:
                        break
                if len(scc) > 1:
                    sccs.append(scc)

        for v in modules:
            if v not in index:
                try:
                    strongconnect(v)
                except RecursionError:
                    logger.warning(
                        f"RecursionError durante análisis de ciclos desde '{v}'. "
                        "El proyecto puede ser demasiado grande para DFS recursivo."
                    )

        return sccs
