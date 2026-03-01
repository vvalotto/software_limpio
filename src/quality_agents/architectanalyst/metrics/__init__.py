"""
Métricas de arquitectura para ArchitectAnalyst.

Cada métrica hereda de ProjectMetric y se auto-descubre via MetricOrchestrator.
"""

from quality_agents.architectanalyst.metrics.abstractness_analyzer import AbstractnessAnalyzer
from quality_agents.architectanalyst.metrics.coupling_analyzer import CouplingAnalyzer
from quality_agents.architectanalyst.metrics.distance_analyzer import DistanceAnalyzer
from quality_agents.architectanalyst.metrics.instability_analyzer import InstabilityAnalyzer

__all__ = [
    "CouplingAnalyzer",
    "InstabilityAnalyzer",
    "AbstractnessAnalyzer",
    "DistanceAnalyzer",
]
