"""
Tipos de datos de ArchitectAnalyst.

Define ArchitectureSeverity, MetricTrend y ArchitectureResult, los tipos propios del agente.
Independientes de los tipos de CodeGuard y DesignReviewer — solo comparte Verifiable de shared/.

Ticket: 1.1
Fecha: 2026-02-28
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ArchitectureSeverity(Enum):
    """Niveles de severidad para los resultados de análisis arquitectónico."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MetricTrend(Enum):
    """
    Tendencia de una métrica respecto al snapshot anterior.

    Solo disponible cuando existe histórico (al menos un análisis previo).
    """

    IMPROVING = "improving"  # La métrica mejoró
    STABLE = "stable"  # La métrica se mantuvo estable
    DEGRADING = "degrading"  # La métrica empeoró

    @property
    def symbol(self) -> str:
        """Símbolo Unicode para mostrar en output."""
        symbols = {
            MetricTrend.IMPROVING: "↓",
            MetricTrend.STABLE: "=",
            MetricTrend.DEGRADING: "↑",
        }
        return symbols[self]


@dataclass
class ArchitectureResult:
    """
    Resultado de un analyzer individual de ArchitectAnalyst.

    Attributes:
        analyzer_name: Nombre del analyzer que generó el resultado.
        metric_name: Nombre de la métrica calculada (ej: "Ca", "Ce", "I", "A", "D").
        module_path: Módulo analizado (Path relativo al proyecto).
        value: Valor medido por el analyzer.
        threshold: Umbral configurado para esta métrica.
                   None para métricas informativas sin umbral (Ca, Ce, A).
        severity: Nivel de severidad (INFO, WARNING, CRITICAL).
        message: Descripción del resultado o problema detectado.
        trend: Tendencia respecto al snapshot anterior. None si no hay histórico.
    """

    analyzer_name: str
    metric_name: str
    module_path: Path
    value: float
    threshold: float | None
    severity: ArchitectureSeverity
    message: str
    trend: MetricTrend | None = None

    def has_violation(self) -> bool:
        """Retorna True si este resultado representa una violación (WARNING o CRITICAL)."""
        return self.severity in (ArchitectureSeverity.WARNING, ArchitectureSeverity.CRITICAL)

    def is_critical(self) -> bool:
        """Retorna True si este resultado es crítico."""
        return self.severity == ArchitectureSeverity.CRITICAL

    def trend_symbol(self) -> str:
        """Retorna el símbolo de tendencia, o '—' si no hay histórico."""
        if self.trend is None:
            return "—"
        return self.trend.symbol

    def __str__(self) -> str:
        threshold_str = f", umbral: {self.threshold}" if self.threshold is not None else ""
        trend_str = f" {self.trend_symbol()}" if self.trend else ""
        return (
            f"[{self.severity.value.upper()}] {self.metric_name}{trend_str} — {self.message} "
            f"(valor: {self.value}{threshold_str}) @ {self.module_path}"
        )
