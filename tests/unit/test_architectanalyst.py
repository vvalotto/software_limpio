"""
Tests unitarios para ArchitectAnalyst.
"""

from datetime import datetime
from pathlib import Path

from quality_agents.architectanalyst import ArchitectAnalyst
from quality_agents.architectanalyst.agent import ArchitectureMetric, ArchitectureSnapshot
from quality_agents.architectanalyst.metrics import (
    calculate_distance_from_main_sequence,
    calculate_instability,
)


class TestArchitectAnalyst:
    """Tests para el agente ArchitectAnalyst."""

    def test_init_default(self):
        """Debe inicializarse con valores por defecto."""
        analyst = ArchitectAnalyst()

        assert analyst.config_path is None
        assert analyst.db_path == Path(".quality_control/architecture.db")
        assert analyst.current_snapshot is None

    def test_init_custom_db(self, tmp_path):
        """Debe aceptar path de DB personalizado."""
        db_path = tmp_path / "custom.db"
        analyst = ArchitectAnalyst(db_path=db_path)

        assert analyst.db_path == db_path

    def test_analyze_returns_snapshot(self, temp_project):
        """analyze() debe retornar ArchitectureSnapshot."""
        analyst = ArchitectAnalyst()
        snapshot = analyst.analyze(temp_project)

        assert isinstance(snapshot, ArchitectureSnapshot)
        assert isinstance(snapshot.timestamp, datetime)
        assert isinstance(snapshot.metrics, dict)
        assert isinstance(snapshot.violations, list)
        assert isinstance(snapshot.dependency_cycles, list)


class TestArchitectureSnapshot:
    """Tests para ArchitectureSnapshot."""

    def test_create_snapshot(self):
        """Debe crear snapshot correctamente."""
        snapshot = ArchitectureSnapshot(
            timestamp=datetime.now(),
            metrics={"instability": 0.5, "distance": 0.1},
            violations=["layer_violation_1"],
            dependency_cycles=[["A", "B", "A"]]
        )

        assert "instability" in snapshot.metrics
        assert len(snapshot.violations) == 1
        assert len(snapshot.dependency_cycles) == 1


class TestMartinMetrics:
    """Tests para métricas de Martin."""

    def test_instability_stable(self):
        """I = 0 cuando Ce = 0 (totalmente estable)."""
        assert calculate_instability(ca=5, ce=0) == 0.0

    def test_instability_unstable(self):
        """I = 1 cuando Ca = 0 (totalmente inestable)."""
        assert calculate_instability(ca=0, ce=5) == 1.0

    def test_instability_balanced(self):
        """I = 0.5 cuando Ca = Ce."""
        assert calculate_instability(ca=5, ce=5) == 0.5

    def test_instability_zero_both(self):
        """I = 0 cuando ambos son 0."""
        assert calculate_instability(ca=0, ce=0) == 0.0

    def test_distance_on_main_sequence(self):
        """D = 0 cuando A + I = 1."""
        # Punto (I=0, A=1) está sobre la línea
        assert calculate_distance_from_main_sequence(0.0, 1.0) == 0.0

        # Punto (I=1, A=0) está sobre la línea
        assert calculate_distance_from_main_sequence(1.0, 0.0) == 0.0

        # Punto (I=0.5, A=0.5) está sobre la línea
        assert calculate_distance_from_main_sequence(0.5, 0.5) == 0.0

    def test_distance_off_main_sequence(self):
        """D > 0 cuando A + I != 1."""
        # Punto (I=0, A=0) - Zona del dolor
        assert calculate_distance_from_main_sequence(0.0, 0.0) == 1.0

        # Punto (I=1, A=1) - Zona inútil
        assert calculate_distance_from_main_sequence(1.0, 1.0) == 1.0


class TestArchitectureMetric:
    """Tests para ArchitectureMetric."""

    def test_create_metric(self):
        """Debe crear métrica correctamente."""
        metric = ArchitectureMetric(
            name="instability",
            value=0.3,
            threshold=0.5,
            trend="stable",
            history=[0.35, 0.32, 0.30]
        )

        assert metric.name == "instability"
        assert metric.value == 0.3
        assert metric.trend == "stable"
        assert len(metric.history) == 3
