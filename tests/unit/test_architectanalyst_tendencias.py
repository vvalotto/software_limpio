"""
Tests unitarios para SnapshotStore y TrendCalculator (Fase 4 de ArchitectAnalyst).

Cubre:
  - SnapshotStore: save, get_latest_results, get_snapshot_count, migración (Ticket 4.1)
  - TrendCalculator: enrich, _classify (Ticket 4.2)
  - Integración: dos análisis consecutivos muestran tendencias correctas (Ticket 4.3)

Ticket: 4.4
Fecha: 2026-03-01
"""

from pathlib import Path

import pytest

from quality_agents.architectanalyst.models import (
    ArchitectureResult,
    ArchitectureSeverity,
    MetricTrend,
)
from quality_agents.architectanalyst.snapshots import SnapshotStore
from quality_agents.architectanalyst.trends import TrendCalculator

# =============================================================================
# Fixtures
# =============================================================================


def _make_result(
    metric_name: str,
    module_path: str,
    value: float,
    severity: ArchitectureSeverity = ArchitectureSeverity.INFO,
    threshold: float | None = None,
) -> ArchitectureResult:
    return ArchitectureResult(
        analyzer_name="TestAnalyzer",
        metric_name=metric_name,
        module_path=Path(module_path),
        value=value,
        threshold=threshold,
        severity=severity,
        message=f"{metric_name}={value}",
    )


@pytest.fixture()
def store(tmp_path: Path) -> SnapshotStore:
    return SnapshotStore(tmp_path / "test.db")


@pytest.fixture()
def result_i_alto() -> ArchitectureResult:
    return _make_result("I", "mipkg/service", 0.9, ArchitectureSeverity.WARNING, 0.8)


@pytest.fixture()
def result_d_critico() -> ArchitectureResult:
    return _make_result("D", "mipkg/core", 0.6, ArchitectureSeverity.CRITICAL, 0.5)


# =============================================================================
# SnapshotStore — Ticket 4.1
# =============================================================================


class TestSnapshotStore:

    def test_init_crea_archivo_db(self, tmp_path: Path) -> None:
        db = tmp_path / "sub" / "arch.db"
        SnapshotStore(db)
        assert db.exists()

    def test_save_retorna_id_entero(self, store: SnapshotStore, result_i_alto: ArchitectureResult) -> None:
        snapshot_id = store.save([result_i_alto])
        assert isinstance(snapshot_id, int)
        assert snapshot_id >= 1

    def test_save_ids_consecutivos(self, store: SnapshotStore, result_i_alto: ArchitectureResult) -> None:
        id1 = store.save([result_i_alto])
        id2 = store.save([result_i_alto])
        assert id2 == id1 + 1

    def test_get_snapshot_count_inicial_cero(self, store: SnapshotStore) -> None:
        assert store.get_snapshot_count() == 0

    def test_get_snapshot_count_incrementa(self, store: SnapshotStore, result_i_alto: ArchitectureResult) -> None:
        store.save([result_i_alto])
        store.save([result_i_alto])
        assert store.get_snapshot_count() == 2

    def test_get_latest_results_none_sin_snapshots(self, store: SnapshotStore) -> None:
        assert store.get_latest_results() is None

    def test_get_latest_results_retorna_ultimo(
        self, store: SnapshotStore, result_i_alto: ArchitectureResult, result_d_critico: ArchitectureResult
    ) -> None:
        store.save([result_i_alto])
        store.save([result_d_critico])
        latest = store.get_latest_results()
        assert latest is not None
        assert len(latest) == 1
        assert latest[0].metric_name == "D"

    def test_save_y_recupera_todos_los_campos(
        self, store: SnapshotStore, result_i_alto: ArchitectureResult
    ) -> None:
        store.save([result_i_alto])
        results = store.get_latest_results()
        assert results is not None
        r = results[0]
        assert r.analyzer_name == result_i_alto.analyzer_name
        assert r.metric_name == result_i_alto.metric_name
        assert str(r.module_path) == str(result_i_alto.module_path)
        assert r.value == pytest.approx(result_i_alto.value)
        assert r.threshold == pytest.approx(result_i_alto.threshold)
        assert r.severity == result_i_alto.severity
        assert r.message == result_i_alto.message

    def test_trend_siempre_none_al_cargar(
        self, store: SnapshotStore, result_i_alto: ArchitectureResult
    ) -> None:
        """El trend no se persiste — siempre None al cargar desde DB."""
        result_i_alto.trend = MetricTrend.IMPROVING
        store.save([result_i_alto])
        results = store.get_latest_results()
        assert results is not None
        assert results[0].trend is None

    def test_save_con_sprint_id(self, store: SnapshotStore, result_i_alto: ArchitectureResult) -> None:
        """sprint_id es opcional — no debe romper el save."""
        snapshot_id = store.save([result_i_alto], sprint_id="sprint-42")
        assert isinstance(snapshot_id, int)

    def test_save_lista_vacia(self, store: SnapshotStore) -> None:
        """Save con lista vacía guarda el snapshot pero sin results."""
        snapshot_id = store.save([])
        assert isinstance(snapshot_id, int)
        results = store.get_latest_results()
        assert results == []

    def test_threshold_none_se_persiste_como_null(self, store: SnapshotStore) -> None:
        r = _make_result("Ca", "mipkg/core", 3.0, threshold=None)
        store.save([r])
        results = store.get_latest_results()
        assert results is not None
        assert results[0].threshold is None

    def test_migracion_schema_legacy(self, tmp_path: Path) -> None:
        """Si existe schema legacy (metrics/violations), lo migra sin error."""
        import sqlite3
        db = tmp_path / "legacy.db"
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE snapshots (id INTEGER PRIMARY KEY, timestamp TEXT)")
            conn.execute("CREATE TABLE metrics (id INTEGER PRIMARY KEY, snapshot_id INTEGER, metric_name TEXT, metric_value REAL)")
            conn.execute("CREATE TABLE violations (id INTEGER PRIMARY KEY, snapshot_id INTEGER, violation_type TEXT, description TEXT)")
            conn.commit()

        # No debe lanzar excepción
        store = SnapshotStore(db)
        assert store.get_snapshot_count() == 0

    def test_multiple_results_en_un_snapshot(self, store: SnapshotStore) -> None:
        results = [
            _make_result("I", "mipkg/a", 0.9),
            _make_result("D", "mipkg/b", 0.4),
            _make_result("Ca", "mipkg/c", 2.0),
        ]
        store.save(results)
        loaded = store.get_latest_results()
        assert loaded is not None
        assert len(loaded) == 3


# =============================================================================
# TrendCalculator — Ticket 4.2
# =============================================================================


class TestTrendCalculator:

    def test_improving_cuando_valor_baja(self) -> None:
        calc = TrendCalculator()
        assert calc._classify(0.5, 0.8) == MetricTrend.IMPROVING

    def test_degrading_cuando_valor_sube(self) -> None:
        calc = TrendCalculator()
        assert calc._classify(0.8, 0.5) == MetricTrend.DEGRADING

    def test_stable_cuando_diferencia_menor_a_tolerance(self) -> None:
        calc = TrendCalculator()
        assert calc._classify(0.5001, 0.5) == MetricTrend.STABLE

    def test_stable_cuando_identico(self) -> None:
        calc = TrendCalculator()
        assert calc._classify(0.5, 0.5) == MetricTrend.STABLE

    def test_enrich_asigna_trend_cuando_hay_previo(self) -> None:
        calc = TrendCalculator()
        current = [_make_result("I", "mipkg/svc", 0.5)]
        previous = [_make_result("I", "mipkg/svc", 0.8)]
        enriched = calc.enrich(current, previous)
        assert enriched[0].trend == MetricTrend.IMPROVING

    def test_enrich_deja_none_si_no_hay_previo(self) -> None:
        calc = TrendCalculator()
        current = [_make_result("I", "mipkg/nuevo", 0.5)]
        previous = [_make_result("I", "mipkg/otro", 0.8)]
        enriched = calc.enrich(current, previous)
        assert enriched[0].trend is None

    def test_enrich_clave_es_metric_name_y_module_path(self) -> None:
        """Misma métrica en módulo diferente no debe hacer match."""
        calc = TrendCalculator()
        current = [_make_result("I", "mipkg/a", 0.3)]
        previous = [_make_result("I", "mipkg/b", 0.8)]
        enriched = calc.enrich(current, previous)
        assert enriched[0].trend is None

    def test_enrich_multiple_resultados(self) -> None:
        calc = TrendCalculator()
        current = [
            _make_result("I", "mipkg/a", 0.3),
            _make_result("D", "mipkg/b", 0.6),
            _make_result("I", "mipkg/c", 0.9),
        ]
        previous = [
            _make_result("I", "mipkg/a", 0.8),   # mejora
            _make_result("D", "mipkg/b", 0.4),   # empeora
        ]
        enriched = calc.enrich(current, previous)
        assert enriched[0].trend == MetricTrend.IMPROVING
        assert enriched[1].trend == MetricTrend.DEGRADING
        assert enriched[2].trend is None  # sin previo

    def test_enrich_con_previous_vacio_no_modifica(self) -> None:
        calc = TrendCalculator()
        current = [_make_result("I", "mipkg/svc", 0.5)]
        enriched = calc.enrich(current, [])
        assert enriched[0].trend is None

    def test_enrich_modifica_los_mismos_objetos(self) -> None:
        """enrich modifica in-place y retorna la misma lista."""
        calc = TrendCalculator()
        current = [_make_result("I", "mipkg/svc", 0.5)]
        previous = [_make_result("I", "mipkg/svc", 0.8)]
        result = calc.enrich(current, previous)
        assert result is current


# =============================================================================
# Integración: dos análisis consecutivos (Ticket 4.3)
# =============================================================================


class TestIntegracionTendencias:

    def test_segundo_analisis_muestra_tendencias(self, tmp_path: Path) -> None:
        """Dos save() consecutivos → el segundo run enriquece con trends."""
        store = SnapshotStore(tmp_path / "arch.db")
        calc = TrendCalculator()

        # Primer análisis
        primer_resultado = [_make_result("I", "mipkg/svc", 0.9)]
        store.save(primer_resultado)

        # Segundo análisis con valor mejorado
        segundo_resultado = [_make_result("I", "mipkg/svc", 0.6)]
        previous = store.get_latest_results()
        assert previous is not None
        enriched = calc.enrich(segundo_resultado, previous)

        assert enriched[0].trend == MetricTrend.IMPROVING

    def test_snapshot_count_crece_con_cada_analisis(self, tmp_path: Path) -> None:
        store = SnapshotStore(tmp_path / "arch.db")
        store.save([_make_result("I", "mipkg/svc", 0.9)])
        store.save([_make_result("I", "mipkg/svc", 0.6)])
        assert store.get_snapshot_count() == 2

    def test_tendencia_stable_sin_cambio(self, tmp_path: Path) -> None:
        store = SnapshotStore(tmp_path / "arch.db")
        calc = TrendCalculator()
        store.save([_make_result("D", "mipkg/core", 0.4)])
        segundo = [_make_result("D", "mipkg/core", 0.4)]
        previous = store.get_latest_results()
        enriched = calc.enrich(segundo, previous)
        assert enriched[0].trend == MetricTrend.STABLE
