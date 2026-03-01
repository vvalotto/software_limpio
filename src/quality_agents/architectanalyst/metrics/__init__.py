"""
Métricas de arquitectura para ArchitectAnalyst.

Cada métrica hereda de ProjectMetric y se auto-descubre via MetricOrchestrator.
"""

from quality_agents.architectanalyst.metrics.abstractness_analyzer import AbstractnessAnalyzer
from quality_agents.architectanalyst.metrics.coupling_analyzer import CouplingAnalyzer
from quality_agents.architectanalyst.metrics.dependency_cycles_analyzer import (
    DependencyCyclesAnalyzer,
)
from quality_agents.architectanalyst.metrics.distance_analyzer import DistanceAnalyzer
from quality_agents.architectanalyst.metrics.instability_analyzer import InstabilityAnalyzer
from quality_agents.architectanalyst.metrics.layer_violations_analyzer import (
    LayerViolationsAnalyzer,
)

__all__ = [
    "DependencyCyclesAnalyzer",
    "LayerViolationsAnalyzer",
    "CouplingAnalyzer",
    "InstabilityAnalyzer",
    "AbstractnessAnalyzer",
    "DistanceAnalyzer",
]
