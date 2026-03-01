"""
TrendCalculator — Comparación de snapshots para calcular tendencias.

Compara los resultados actuales contra el snapshot anterior almacenado
en SQLite y asigna a cada ArchitectureResult su MetricTrend:

  IMPROVING: el valor bajó respecto al anterior (métrica mejoró)
  STABLE:    el valor se mantuvo (diferencia < TOLERANCE)
  DEGRADING: el valor subió respecto al anterior (métrica empeoró)

La interpretación "bajar = mejorar" es válida para todas las métricas
del agente: I (inestabilidad), D (distancia), Ca, Ce — valores menores
indican sistemas más saludables.

Si un módulo o métrica no existe en el snapshot anterior (es nuevo),
su trend queda en None (sin histórico comparable).

Ticket: 4.2
Fecha: 2026-03-01
"""

from typing import Dict, List, Tuple

from quality_agents.architectanalyst.models import ArchitectureResult, MetricTrend


class TrendCalculator:
    """
    Calcula tendencias comparando resultados actuales vs snapshot anterior.

    Attributes:
        TOLERANCE: Diferencia mínima entre valores para considerar un cambio.
                   Diferencias menores se clasifican como STABLE.
    """

    TOLERANCE: float = 0.001

    def enrich(
        self,
        current: List[ArchitectureResult],
        previous: List[ArchitectureResult],
    ) -> List[ArchitectureResult]:
        """
        Agrega el campo `trend` a cada resultado comparando con el snapshot anterior.

        Clave de comparación: (metric_name, str(module_path)).
        Si no hay resultado previo para esa clave, trend queda en None.

        Args:
            current: Resultados del análisis actual (trend=None).
            previous: Resultados del snapshot anterior cargados desde SQLite.

        Returns:
            Lista de resultados con trend asignado donde hay histórico.
        """
        previous_map: Dict[Tuple[str, str], float] = {
            (r.metric_name, str(r.module_path)): r.value
            for r in previous
        }

        for result in current:
            key = (result.metric_name, str(result.module_path))
            if key in previous_map:
                result.trend = self._classify(result.value, previous_map[key])

        return current

    # -------------------------------------------------------------------------
    # Helpers privados
    # -------------------------------------------------------------------------

    def _classify(self, current_value: float, previous_value: float) -> MetricTrend:
        """
        Clasifica la dirección del cambio entre dos valores.

        Args:
            current_value: Valor medido en el análisis actual.
            previous_value: Valor del snapshot anterior.

        Returns:
            IMPROVING si bajó, DEGRADING si subió, STABLE si es prácticamente igual.
        """
        diff = current_value - previous_value

        if abs(diff) < self.TOLERANCE:
            return MetricTrend.STABLE
        elif diff < 0:
            return MetricTrend.IMPROVING
        else:
            return MetricTrend.DEGRADING
