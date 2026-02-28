"""
Tests unitarios para ArchitectureSeverity, MetricTrend, ArchitectureResult
y las funciones matemáticas de metrics/_utils.py.

Ticket: 1.6
"""

from pathlib import Path

import pytest

from quality_agents.architectanalyst.metrics._utils import (
    calculate_distance,
    calculate_instability,
)
from quality_agents.architectanalyst.models import (
    ArchitectureResult,
    ArchitectureSeverity,
    MetricTrend,
)


class TestArchitectureSeverity:
    """Tests para el enum ArchitectureSeverity."""

    def test_valores(self):
        """Debe tener los tres niveles de severidad correctos."""
        assert ArchitectureSeverity.INFO.value == "info"
        assert ArchitectureSeverity.WARNING.value == "warning"
        assert ArchitectureSeverity.CRITICAL.value == "critical"

    def test_exactamente_tres_niveles(self):
        """Debe haber exactamente tres niveles."""
        assert len(ArchitectureSeverity) == 3

    def test_comparacion_por_identidad(self):
        """Los valores del enum son comparables por identidad."""
        assert ArchitectureSeverity.INFO is ArchitectureSeverity.INFO
        assert ArchitectureSeverity.WARNING is not ArchitectureSeverity.CRITICAL


class TestMetricTrend:
    """Tests para el enum MetricTrend."""

    def test_valores(self):
        """Debe tener los tres estados de tendencia correctos."""
        assert MetricTrend.IMPROVING.value == "improving"
        assert MetricTrend.STABLE.value == "stable"
        assert MetricTrend.DEGRADING.value == "degrading"

    def test_exactamente_tres_estados(self):
        """Debe haber exactamente tres estados."""
        assert len(MetricTrend) == 3

    def test_simbolo_improving(self):
        """IMPROVING debe mostrar ↓ (la métrica bajó — mejoró)."""
        assert MetricTrend.IMPROVING.symbol == "↓"

    def test_simbolo_stable(self):
        """STABLE debe mostrar =."""
        assert MetricTrend.STABLE.symbol == "="

    def test_simbolo_degrading(self):
        """DEGRADING debe mostrar ↑ (la métrica subió — empeoró)."""
        assert MetricTrend.DEGRADING.symbol == "↑"


class TestArchitectureResultCampos:
    """Tests para los campos del dataclass ArchitectureResult."""

    def _resultado_info(self, **kwargs) -> ArchitectureResult:
        """Fixture: resultado informativo sin umbral (Ca)."""
        defaults = dict(
            analyzer_name="CouplingAnalyzer",
            metric_name="Ca",
            module_path=Path("src/domain/service.py"),
            value=3.0,
            threshold=None,
            severity=ArchitectureSeverity.INFO,
            message="3 módulos dependen de este",
        )
        defaults.update(kwargs)
        return ArchitectureResult(**defaults)

    def test_campos_requeridos(self):
        """Debe instanciarse correctamente con todos los campos requeridos."""
        r = self._resultado_info()

        assert r.analyzer_name == "CouplingAnalyzer"
        assert r.metric_name == "Ca"
        assert r.module_path == Path("src/domain/service.py")
        assert r.value == 3.0
        assert r.threshold is None
        assert r.severity == ArchitectureSeverity.INFO
        assert r.message == "3 módulos dependen de este"

    def test_trend_none_por_defecto(self):
        """trend debe ser None por defecto (sin histórico)."""
        r = self._resultado_info()

        assert r.trend is None

    def test_trend_con_valor(self):
        """Debe aceptar trend con valor de MetricTrend."""
        r = self._resultado_info(trend=MetricTrend.DEGRADING)

        assert r.trend == MetricTrend.DEGRADING

    def test_threshold_none_para_metrica_informativa(self):
        """threshold=None es válido para métricas sin umbral (Ca, Ce, A)."""
        r = self._resultado_info(metric_name="Ca", threshold=None)

        assert r.threshold is None

    def test_threshold_con_valor_para_metrica_con_umbral(self):
        """threshold con valor para métricas con umbral (I, D)."""
        r = ArchitectureResult(
            analyzer_name="InstabilityAnalyzer",
            metric_name="I",
            module_path=Path("src/module.py"),
            value=0.85,
            threshold=0.8,
            severity=ArchitectureSeverity.WARNING,
            message="Módulo inestable",
        )

        assert r.threshold == 0.8


class TestArchitectureResultHasViolation:
    """Tests para has_violation() e is_critical()."""

    def _resultado(self, severity: ArchitectureSeverity) -> ArchitectureResult:
        return ArchitectureResult(
            analyzer_name="TestAnalyzer",
            metric_name="D",
            module_path=Path("src/foo.py"),
            value=0.4,
            threshold=0.3,
            severity=severity,
            message="Mensaje de prueba",
        )

    def test_info_no_es_violacion(self):
        """INFO no debe ser considerado una violación."""
        assert not self._resultado(ArchitectureSeverity.INFO).has_violation()

    def test_warning_es_violacion(self):
        """WARNING debe ser considerado una violación."""
        assert self._resultado(ArchitectureSeverity.WARNING).has_violation()

    def test_critical_es_violacion(self):
        """CRITICAL debe ser considerado una violación."""
        assert self._resultado(ArchitectureSeverity.CRITICAL).has_violation()

    def test_info_no_es_critical(self):
        """INFO no debe ser crítico."""
        assert not self._resultado(ArchitectureSeverity.INFO).is_critical()

    def test_warning_no_es_critical(self):
        """WARNING no debe ser crítico."""
        assert not self._resultado(ArchitectureSeverity.WARNING).is_critical()

    def test_critical_es_critical(self):
        """CRITICAL debe ser crítico."""
        assert self._resultado(ArchitectureSeverity.CRITICAL).is_critical()


class TestArchitectureResultTrendSymbol:
    """Tests para trend_symbol()."""

    def _resultado(self, trend=None) -> ArchitectureResult:
        return ArchitectureResult(
            analyzer_name="DistanceAnalyzer",
            metric_name="D",
            module_path=Path("src/foo.py"),
            value=0.4,
            threshold=0.3,
            severity=ArchitectureSeverity.WARNING,
            message="Distancia elevada",
            trend=trend,
        )

    def test_sin_historial_retorna_guion(self):
        """Sin histórico (trend=None) debe retornar '—'."""
        assert self._resultado(trend=None).trend_symbol() == "—"

    def test_improving_retorna_flecha_abajo(self):
        assert self._resultado(trend=MetricTrend.IMPROVING).trend_symbol() == "↓"

    def test_stable_retorna_igual(self):
        assert self._resultado(trend=MetricTrend.STABLE).trend_symbol() == "="

    def test_degrading_retorna_flecha_arriba(self):
        assert self._resultado(trend=MetricTrend.DEGRADING).trend_symbol() == "↑"


class TestArchitectureResultStr:
    """Tests para la representación __str__ de ArchitectureResult."""

    def test_str_incluye_campos_clave(self):
        """__str__ debe incluir métrica, severidad, mensaje y path."""
        r = ArchitectureResult(
            analyzer_name="InstabilityAnalyzer",
            metric_name="I",
            module_path=Path("src/service.py"),
            value=0.85,
            threshold=0.8,
            severity=ArchitectureSeverity.WARNING,
            message="Módulo extremadamente inestable",
        )

        texto = str(r)
        assert "WARNING" in texto
        assert "I" in texto
        assert "Módulo extremadamente inestable" in texto
        assert "0.85" in texto
        assert "src/service.py" in texto

    def test_str_incluye_umbral_si_existe(self):
        """__str__ debe incluir el umbral cuando no es None."""
        r = ArchitectureResult(
            analyzer_name="DistanceAnalyzer",
            metric_name="D",
            module_path=Path("src/foo.py"),
            value=0.55,
            threshold=0.5,
            severity=ArchitectureSeverity.CRITICAL,
            message="Zone of Pain",
        )

        assert "0.5" in str(r)

    def test_str_sin_umbral_no_incluye_texto_umbral(self):
        """__str__ no debe incluir 'umbral' cuando threshold es None."""
        r = ArchitectureResult(
            analyzer_name="CouplingAnalyzer",
            metric_name="Ca",
            module_path=Path("src/foo.py"),
            value=5.0,
            threshold=None,
            severity=ArchitectureSeverity.INFO,
            message="5 dependientes",
        )

        assert "umbral" not in str(r)

    def test_str_incluye_simbolo_trend(self):
        """__str__ debe incluir el símbolo de tendencia cuando hay histórico."""
        r = ArchitectureResult(
            analyzer_name="InstabilityAnalyzer",
            metric_name="I",
            module_path=Path("src/foo.py"),
            value=0.85,
            threshold=0.8,
            severity=ArchitectureSeverity.WARNING,
            message="Inestable",
            trend=MetricTrend.DEGRADING,
        )

        assert "↑" in str(r)


# ========== Tests de funciones matemáticas ==========


class TestCalculateInstability:
    """Tests para calculate_instability(ca, ce)."""

    def test_totalmente_estable(self):
        """I = 0 cuando Ce = 0 (nada depende de él pero él no depende de nada)."""
        assert calculate_instability(ca=5, ce=0) == 0.0

    def test_totalmente_inestable(self):
        """I = 1 cuando Ca = 0 (nadie depende de él)."""
        assert calculate_instability(ca=0, ce=5) == 1.0

    def test_equilibrado(self):
        """I = 0.5 cuando Ca = Ce."""
        assert calculate_instability(ca=5, ce=5) == 0.5

    def test_ambos_cero_retorna_cero(self):
        """I = 0 cuando ca = ce = 0 (módulo aislado)."""
        assert calculate_instability(ca=0, ce=0) == 0.0

    def test_valores_asimetricos(self):
        """Verifica el cálculo con valores asimétricos."""
        assert calculate_instability(ca=3, ce=1) == pytest.approx(0.25)
        assert calculate_instability(ca=1, ce=3) == pytest.approx(0.75)

    def test_resultado_en_rango_valido(self):
        """El resultado siempre debe estar en [0.0, 1.0]."""
        for ca, ce in [(0, 10), (10, 0), (5, 5), (3, 7), (0, 0)]:
            result = calculate_instability(ca, ce)
            assert 0.0 <= result <= 1.0


class TestCalculateDistance:
    """Tests para calculate_distance(instability, abstractness)."""

    def test_sobre_la_linea_i0_a1(self):
        """D = 0 cuando I=0, A=1 (estable y abstracto — ideal)."""
        assert calculate_distance(instability=0.0, abstractness=1.0) == pytest.approx(0.0)

    def test_sobre_la_linea_i1_a0(self):
        """D = 0 cuando I=1, A=0 (inestable y concreto — ideal)."""
        assert calculate_distance(instability=1.0, abstractness=0.0) == pytest.approx(0.0)

    def test_sobre_la_linea_centro(self):
        """D = 0 cuando I=0.5, A=0.5 (centro de la Main Sequence)."""
        assert calculate_distance(instability=0.5, abstractness=0.5) == pytest.approx(0.0)

    def test_zone_of_pain(self):
        """D = 1 cuando I=0, A=0 (estable y concreto — Zone of Pain)."""
        assert calculate_distance(instability=0.0, abstractness=0.0) == pytest.approx(1.0)

    def test_zone_of_uselessness(self):
        """D = 1 cuando I=1, A=1 (inestable y abstracto — Zone of Uselessness)."""
        assert calculate_distance(instability=1.0, abstractness=1.0) == pytest.approx(1.0)

    def test_resultado_en_rango_valido(self):
        """El resultado siempre debe estar en [0.0, 1.0]."""
        casos = [(0.0, 0.0), (1.0, 1.0), (0.5, 0.5), (0.3, 0.4), (0.8, 0.1)]
        for i, a in casos:
            result = calculate_distance(i, a)
            assert 0.0 <= result <= 1.0

    def test_simetria(self):
        """D(I, A) == D(A, I) — la distancia es simétrica respecto a la línea."""
        assert calculate_distance(0.3, 0.6) == pytest.approx(calculate_distance(0.6, 0.3))
