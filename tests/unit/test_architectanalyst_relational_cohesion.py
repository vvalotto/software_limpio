"""Tests unitarios para RelationalCohesionAnalyzer (#57)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quality_agents.architectanalyst.config import (
    ArchitectAnalystChecksConfig,
    ArchitectAnalystConfig,
)
from quality_agents.architectanalyst.metrics.relational_cohesion_analyzer import (
    RelationalCohesionAnalyzer,
)
from quality_agents.architectanalyst.models import ArchitectureSeverity


def _config(min_h=1.5, depth=1, enabled=True):
    cfg = ArchitectAnalystConfig(
        min_relational_cohesion=min_h,
        analysis_depth=depth,
        checks=ArchitectAnalystChecksConfig(relational_cohesion=enabled),
    )
    return cfg


def _mock_graph(modules, efferent_map=None):
    efferent_map = efferent_map or {}
    graph = MagicMock()
    graph.modules = set(modules)
    graph.efferent_coupling.side_effect = lambda m: efferent_map.get(m, [])
    return graph


class TestRelationalCohesionAnalyzerProperties:
    def test_name(self):
        assert RelationalCohesionAnalyzer().name == "RelationalCohesionAnalyzer"

    def test_category(self):
        assert RelationalCohesionAnalyzer().category == "martin"

    def test_priority(self):
        assert RelationalCohesionAnalyzer().priority == 9

    def test_estimated_duration(self):
        assert RelationalCohesionAnalyzer().estimated_duration == 3.0


class TestRelationalCohesionShouldRun:
    def test_runs_by_default(self):
        a = RelationalCohesionAnalyzer()
        assert a.should_run(_config()) is True

    def test_skips_when_toggle_disabled(self):
        a = RelationalCohesionAnalyzer()
        assert a.should_run(_config(enabled=False)) is False

    def test_runs_when_toggle_enabled(self):
        a = RelationalCohesionAnalyzer()
        assert a.should_run(_config(enabled=True)) is True


class TestComputePackageMetrics:
    def test_single_module_no_relations(self):
        graph = _mock_graph(["pkg.a"])
        a = RelationalCohesionAnalyzer()
        result = a._compute_package_metrics(graph, {}, depth=1)
        assert result["pkg"]["r_relations"] == 0

    def test_internal_relation_counted(self):
        graph = _mock_graph(
            ["pkg.a", "pkg.b"],
            efferent_map={"pkg.a": ["pkg.b"]},
        )
        a = RelationalCohesionAnalyzer()
        result = a._compute_package_metrics(graph, {}, depth=1)
        assert result["pkg"]["r_relations"] == 1

    def test_external_relation_not_counted(self):
        graph = _mock_graph(
            ["pkg.a", "other.b"],
            efferent_map={"pkg.a": ["other.b"]},
        )
        a = RelationalCohesionAnalyzer()
        result = a._compute_package_metrics(graph, {}, depth=1)
        assert result["pkg"]["r_relations"] == 0

    def test_bidirectional_relations_counted_separately(self):
        graph = _mock_graph(
            ["pkg.a", "pkg.b"],
            efferent_map={"pkg.a": ["pkg.b"], "pkg.b": ["pkg.a"]},
        )
        a = RelationalCohesionAnalyzer()
        result = a._compute_package_metrics(graph, {}, depth=1)
        assert result["pkg"]["r_relations"] == 2

    def test_depth_2_groups_correctly(self):
        graph = _mock_graph(
            ["myapp.domain.a", "myapp.domain.b"],
            efferent_map={"myapp.domain.a": ["myapp.domain.b"]},
        )
        a = RelationalCohesionAnalyzer()
        result = a._compute_package_metrics(graph, {}, depth=2)
        assert result["myapp.domain"]["r_relations"] == 1


class TestRelationalCohesionExecute:
    def test_no_result_when_package_has_fewer_than_2_classes(self, tmp_path):
        a = RelationalCohesionAnalyzer()
        a._config = _config()

        with patch.object(a, "_compute_package_metrics", return_value={
            "mypkg": {"n_types": 1, "r_relations": 0}
        }), patch(
            "quality_agents.architectanalyst.metrics.relational_cohesion_analyzer.DependencyGraphBuilder"
        ) as MockB:
            MockB.return_value.build.return_value = MagicMock(modules=set())
            results = a.analyze(tmp_path, [])

        assert results == []

    def test_warning_when_h_below_threshold(self, tmp_path):
        a = RelationalCohesionAnalyzer()
        a._config = _config(min_h=1.5)

        # H = (0 + 1) / 3 = 0.33 < 1.5 → warning
        with patch.object(a, "_compute_package_metrics", return_value={
            "mypkg": {"n_types": 3, "r_relations": 0}
        }), patch(
            "quality_agents.architectanalyst.metrics.relational_cohesion_analyzer.DependencyGraphBuilder"
        ) as MockB:
            MockB.return_value.build.return_value = MagicMock(modules=set())
            results = a.analyze(tmp_path, [])

        assert len(results) == 1
        assert results[0].severity == ArchitectureSeverity.WARNING
        assert results[0].metric_name == "H"

    def test_no_result_when_h_above_threshold(self, tmp_path):
        a = RelationalCohesionAnalyzer()
        a._config = _config(min_h=1.5)

        # H = (5 + 1) / 3 = 2.0 >= 1.5 → no warning
        with patch.object(a, "_compute_package_metrics", return_value={
            "mypkg": {"n_types": 3, "r_relations": 5}
        }), patch(
            "quality_agents.architectanalyst.metrics.relational_cohesion_analyzer.DependencyGraphBuilder"
        ) as MockB:
            MockB.return_value.build.return_value = MagicMock(modules=set())
            results = a.analyze(tmp_path, [])

        assert results == []

    def test_h_value_in_result(self, tmp_path):
        a = RelationalCohesionAnalyzer()
        a._config = _config(min_h=1.5)

        # H = (1 + 1) / 4 = 0.5
        with patch.object(a, "_compute_package_metrics", return_value={
            "mypkg": {"n_types": 4, "r_relations": 1}
        }), patch(
            "quality_agents.architectanalyst.metrics.relational_cohesion_analyzer.DependencyGraphBuilder"
        ) as MockB:
            MockB.return_value.build.return_value = MagicMock(modules=set())
            results = a.analyze(tmp_path, [])

        assert results[0].value == pytest.approx(0.5, abs=0.01)

    def test_message_contains_h_r_n(self, tmp_path):
        a = RelationalCohesionAnalyzer()
        a._config = _config(min_h=1.5)

        with patch.object(a, "_compute_package_metrics", return_value={
            "mypkg": {"n_types": 3, "r_relations": 0}
        }), patch(
            "quality_agents.architectanalyst.metrics.relational_cohesion_analyzer.DependencyGraphBuilder"
        ) as MockB:
            MockB.return_value.build.return_value = MagicMock(modules=set())
            results = a.analyze(tmp_path, [])

        assert "R=0" in results[0].message
        assert "N=3" in results[0].message


class TestRelationalCohesionConfig:
    def test_default_min_relational_cohesion(self):
        assert ArchitectAnalystConfig().min_relational_cohesion == 1.5

    def test_default_toggle_enabled(self):
        assert ArchitectAnalystConfig().checks.relational_cohesion is True

    def test_from_pyproject_toml_loads_min_relational_cohesion(self, tmp_path):
        toml = tmp_path / "pyproject.toml"
        toml.write_text(
            "[tool.architectanalyst]\n"
            "min_relational_cohesion = 2.0\n"
        )
        config = ArchitectAnalystConfig.from_pyproject_toml(toml)
        assert config.min_relational_cohesion == 2.0
