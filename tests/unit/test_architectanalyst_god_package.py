"""Tests unitarios para GodPackageAnalyzer (#58)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quality_agents.architectanalyst.config import (
    ArchitectAnalystChecksConfig,
    ArchitectAnalystConfig,
)
from quality_agents.architectanalyst.metrics.god_package_analyzer import GodPackageAnalyzer
from quality_agents.architectanalyst.models import ArchitectureSeverity


def _config(max_classes=20, max_ca=10, depth=1, enabled=True):
    return ArchitectAnalystConfig(
        max_package_classes=max_classes,
        max_package_ca=max_ca,
        analysis_depth=depth,
        checks=ArchitectAnalystChecksConfig(god_package=enabled),
    )


def _mock_graph(modules, efferent_map=None):
    efferent_map = efferent_map or {}
    graph = MagicMock()
    graph.modules = set(modules)
    graph.efferent_coupling.side_effect = lambda m: efferent_map.get(m, [])
    return graph


class TestGodPackageAnalyzerProperties:
    def test_name(self):
        assert GodPackageAnalyzer().name == "GodPackageAnalyzer"

    def test_category(self):
        assert GodPackageAnalyzer().category == "smells"

    def test_priority(self):
        assert GodPackageAnalyzer().priority == 10

    def test_estimated_duration(self):
        assert GodPackageAnalyzer().estimated_duration == 3.0


class TestGodPackageShouldRun:
    def test_runs_by_default(self):
        a = GodPackageAnalyzer()
        assert a.should_run(_config()) is True

    def test_skips_when_toggle_disabled(self):
        a = GodPackageAnalyzer()
        assert a.should_run(_config(enabled=False)) is False

    def test_runs_when_toggle_enabled(self):
        a = GodPackageAnalyzer()
        assert a.should_run(_config(enabled=True)) is True


class TestComputePackageData:
    def test_empty_graph_returns_empty(self):
        graph = _mock_graph([])
        a = GodPackageAnalyzer()
        result = a._compute_package_data(graph, {}, depth=1)
        assert result == {}

    def test_single_module_no_ca(self):
        graph = _mock_graph(["pkg.a"])
        a = GodPackageAnalyzer()
        result = a._compute_package_data(graph, {}, depth=1)
        assert result["pkg"]["ca"] == 0

    def test_ca_counted_when_other_package_imports(self):
        graph = _mock_graph(
            ["pkg.a", "other.b"],
            efferent_map={"other.b": ["pkg.a"]},
        )
        a = GodPackageAnalyzer()
        result = a._compute_package_data(graph, {}, depth=1)
        assert result["pkg"]["ca"] == 1
        assert result["other"]["ca"] == 0

    def test_ca_counts_distinct_packages_not_modules(self):
        # Dos módulos del mismo paquete importan pkg.a → Ca=1, no 2
        graph = _mock_graph(
            ["pkg.a", "other.b", "other.c"],
            efferent_map={"other.b": ["pkg.a"], "other.c": ["pkg.a"]},
        )
        a = GodPackageAnalyzer()
        result = a._compute_package_data(graph, {}, depth=1)
        assert result["pkg"]["ca"] == 1

    def test_internal_imports_not_counted_in_ca(self):
        graph = _mock_graph(
            ["pkg.a", "pkg.b"],
            efferent_map={"pkg.a": ["pkg.b"]},
        )
        a = GodPackageAnalyzer()
        result = a._compute_package_data(graph, {}, depth=1)
        assert result["pkg"]["ca"] == 0

    def test_depth_2_groups_correctly(self):
        graph = _mock_graph(
            ["myapp.domain.a", "myapp.infra.b"],
            efferent_map={"myapp.infra.b": ["myapp.domain.a"]},
        )
        a = GodPackageAnalyzer()
        result = a._compute_package_data(graph, {}, depth=2)
        assert result["myapp.domain"]["ca"] == 1
        assert result["myapp.infra"]["ca"] == 0

    def test_n_classes_zero_when_no_file(self):
        graph = _mock_graph(["pkg.a"])
        a = GodPackageAnalyzer()
        result = a._compute_package_data(graph, {}, depth=1)
        assert result["pkg"]["n_classes"] == 0

    def test_multiple_ca_packages(self):
        graph = _mock_graph(
            ["core.a", "svc1.b", "svc2.c", "svc3.d"],
            efferent_map={
                "svc1.b": ["core.a"],
                "svc2.c": ["core.a"],
                "svc3.d": ["core.a"],
            },
        )
        a = GodPackageAnalyzer()
        result = a._compute_package_data(graph, {}, depth=1)
        assert result["core"]["ca"] == 3


class TestGodPackageAnalyze:
    def test_no_result_below_both_thresholds(self, tmp_path):
        a = GodPackageAnalyzer()
        a._config = _config(max_classes=20, max_ca=10)

        with patch.object(a, "_compute_package_data", return_value={
            "mypkg": {"n_classes": 5, "ca": 3}
        }), patch(
            "quality_agents.architectanalyst.metrics.god_package_analyzer.DependencyGraphBuilder"
        ) as MockB:
            MockB.return_value.build.return_value = MagicMock(modules=set())
            results = a.analyze(tmp_path, [])

        assert results == []

    def test_warning_when_classes_exceed_threshold(self, tmp_path):
        a = GodPackageAnalyzer()
        a._config = _config(max_classes=10, max_ca=100)

        with patch.object(a, "_compute_package_data", return_value={
            "mypkg": {"n_classes": 25, "ca": 2}
        }), patch(
            "quality_agents.architectanalyst.metrics.god_package_analyzer.DependencyGraphBuilder"
        ) as MockB:
            MockB.return_value.build.return_value = MagicMock(modules=set())
            results = a.analyze(tmp_path, [])

        assert len(results) == 1
        assert results[0].metric_name == "GodPackage.Classes"
        assert results[0].severity == ArchitectureSeverity.WARNING
        assert results[0].value == 25.0

    def test_warning_when_ca_exceeds_threshold(self, tmp_path):
        a = GodPackageAnalyzer()
        a._config = _config(max_classes=100, max_ca=5)

        with patch.object(a, "_compute_package_data", return_value={
            "mypkg": {"n_classes": 3, "ca": 12}
        }), patch(
            "quality_agents.architectanalyst.metrics.god_package_analyzer.DependencyGraphBuilder"
        ) as MockB:
            MockB.return_value.build.return_value = MagicMock(modules=set())
            results = a.analyze(tmp_path, [])

        assert len(results) == 1
        assert results[0].metric_name == "GodPackage.Ca"
        assert results[0].severity == ArchitectureSeverity.WARNING
        assert results[0].value == 12.0

    def test_two_warnings_when_both_exceed_threshold(self, tmp_path):
        a = GodPackageAnalyzer()
        a._config = _config(max_classes=10, max_ca=5)

        with patch.object(a, "_compute_package_data", return_value={
            "mypkg": {"n_classes": 30, "ca": 15}
        }), patch(
            "quality_agents.architectanalyst.metrics.god_package_analyzer.DependencyGraphBuilder"
        ) as MockB:
            MockB.return_value.build.return_value = MagicMock(modules=set())
            results = a.analyze(tmp_path, [])

        assert len(results) == 2
        metric_names = {r.metric_name for r in results}
        assert metric_names == {"GodPackage.Classes", "GodPackage.Ca"}

    def test_message_contains_package_name_and_values(self, tmp_path):
        a = GodPackageAnalyzer()
        a._config = _config(max_classes=10, max_ca=100)

        with patch.object(a, "_compute_package_data", return_value={
            "mypkg": {"n_classes": 25, "ca": 2}
        }), patch(
            "quality_agents.architectanalyst.metrics.god_package_analyzer.DependencyGraphBuilder"
        ) as MockB:
            MockB.return_value.build.return_value = MagicMock(modules=set())
            results = a.analyze(tmp_path, [])

        assert "mypkg" in results[0].message
        assert "25" in results[0].message

    def test_exactly_at_threshold_no_warning(self, tmp_path):
        a = GodPackageAnalyzer()
        a._config = _config(max_classes=20, max_ca=10)

        with patch.object(a, "_compute_package_data", return_value={
            "mypkg": {"n_classes": 20, "ca": 10}
        }), patch(
            "quality_agents.architectanalyst.metrics.god_package_analyzer.DependencyGraphBuilder"
        ) as MockB:
            MockB.return_value.build.return_value = MagicMock(modules=set())
            results = a.analyze(tmp_path, [])

        assert results == []


class TestGodPackageConfig:
    def test_default_max_package_classes(self):
        assert ArchitectAnalystConfig().max_package_classes == 20

    def test_default_max_package_ca(self):
        assert ArchitectAnalystConfig().max_package_ca == 10

    def test_default_toggle_enabled(self):
        assert ArchitectAnalystConfig().checks.god_package is True

    def test_from_pyproject_toml_loads_max_package_classes(self, tmp_path):
        toml = tmp_path / "pyproject.toml"
        toml.write_text(
            "[tool.architectanalyst]\n"
            "max_package_classes = 30\n"
        )
        config = ArchitectAnalystConfig.from_pyproject_toml(toml)
        assert config.max_package_classes == 30

    def test_from_pyproject_toml_loads_max_package_ca(self, tmp_path):
        toml = tmp_path / "pyproject.toml"
        toml.write_text(
            "[tool.architectanalyst]\n"
            "max_package_ca = 15\n"
        )
        config = ArchitectAnalystConfig.from_pyproject_toml(toml)
        assert config.max_package_ca == 15
