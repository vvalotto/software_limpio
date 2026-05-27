"""Tests unitarios para analysis_depth en DistanceAnalyzer (#48)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quality_agents.architectanalyst.config import ArchitectAnalystConfig
from quality_agents.architectanalyst.metrics.distance_analyzer import DistanceAnalyzer


def _config(analysis_depth=1, warn=0.3, crit=0.5):
    cfg = ArchitectAnalystConfig(
        max_distance_warning=warn,
        max_distance_critical=crit,
        analysis_depth=analysis_depth,
    )
    return cfg


def _mock_graph(modules, efferent_map=None):
    """
    modules: lista de nombres de módulo
    efferent_map: {module: [deps]} — dependencias efferentes por módulo
    """
    efferent_map = efferent_map or {}
    graph = MagicMock()
    graph.modules = set(modules)
    graph.efferent_coupling.side_effect = lambda m: efferent_map.get(m, [])
    graph.afferent_coupling.side_effect = lambda m: []
    return graph


class TestAggregateToPackagesDepth:
    def _analyzer(self):
        a = DistanceAnalyzer()
        a._config = _config()
        return a

    def test_depth_1_groups_by_first_component(self):
        graph = _mock_graph(["myapp.domain.model", "myapp.domain.repo"])
        result = self._analyzer()._aggregate_to_packages(graph, {}, depth=1)
        assert "myapp" in result
        assert "myapp.domain" not in result

    def test_depth_2_groups_by_two_components(self):
        graph = _mock_graph(["myapp.domain.model", "myapp.infra.db"])
        result = self._analyzer()._aggregate_to_packages(graph, {}, depth=2)
        assert "myapp.domain" in result
        assert "myapp.infra" in result
        assert "myapp" not in result

    def test_depth_2_separates_subpackages(self):
        graph = _mock_graph([
            "myapp.domain.model",
            "myapp.application.service",
        ])
        result = self._analyzer()._aggregate_to_packages(graph, {}, depth=2)
        assert "myapp.domain" in result
        assert "myapp.application" in result
        assert len(result) == 2

    def test_depth_1_default_behavior_unchanged(self):
        graph = _mock_graph(["a.b.c", "a.b.d", "x.y"])
        result = self._analyzer()._aggregate_to_packages(graph, {}, depth=1)
        assert set(result.keys()) == {"a", "x"}

    def test_depth_greater_than_module_length_uses_full_name(self):
        # module "a" split con depth=3 → ["a"] → pkg = "a"
        graph = _mock_graph(["a"])
        result = self._analyzer()._aggregate_to_packages(graph, {}, depth=3)
        assert "a" in result

    def test_ce_computed_between_packages_at_depth_2(self):
        # myapp.domain.model depende de myapp.infra.db
        graph = _mock_graph(
            ["myapp.domain.model", "myapp.infra.db"],
            efferent_map={"myapp.domain.model": ["myapp.infra.db"]},
        )
        result = self._analyzer()._aggregate_to_packages(graph, {}, depth=2)
        assert result["myapp.domain"]["ce"] == 1
        assert result["myapp.infra"]["ca"] == 1

    def test_ce_not_counted_within_same_package_at_depth_2(self):
        # myapp.domain.model depende de myapp.domain.repo → mismo paquete
        graph = _mock_graph(
            ["myapp.domain.model", "myapp.domain.repo"],
            efferent_map={"myapp.domain.model": ["myapp.domain.repo"]},
        )
        result = self._analyzer()._aggregate_to_packages(graph, {}, depth=2)
        assert result["myapp.domain"]["ce"] == 0


class TestAnalysisDepthConfig:
    def test_default_analysis_depth_is_1(self):
        config = ArchitectAnalystConfig()
        assert config.analysis_depth == 1

    def test_analysis_depth_can_be_set(self):
        config = ArchitectAnalystConfig(analysis_depth=2)
        assert config.analysis_depth == 2

    def test_from_pyproject_toml_loads_analysis_depth(self, tmp_path):
        toml = tmp_path / "pyproject.toml"
        toml.write_text(
            "[tool.architectanalyst]\n"
            "analysis_depth = 2\n"
        )
        config = ArchitectAnalystConfig.from_pyproject_toml(toml)
        assert config.analysis_depth == 2


class TestDistanceAnalyzerUsesDepth:
    def test_analyze_passes_depth_to_aggregator(self, tmp_path):
        analyzer = DistanceAnalyzer()
        analyzer._config = _config(analysis_depth=2)

        with patch.object(
            analyzer, "_aggregate_to_packages", wraps=analyzer._aggregate_to_packages
        ) as mock_agg, patch(
            "quality_agents.architectanalyst.metrics.distance_analyzer.DependencyGraphBuilder"
        ) as MockBuilder:
            MockBuilder.return_value.build.return_value = _mock_graph([])
            analyzer.analyze(tmp_path, [])

        mock_agg.assert_called_once()
        _, kwargs = mock_agg.call_args
        assert kwargs.get("depth", mock_agg.call_args[0][2] if len(mock_agg.call_args[0]) > 2 else 1) == 2

    def test_depth_1_produces_same_results_as_before(self, tmp_path):
        """Con depth=1 el comportamiento es idéntico al original."""
        analyzer = DistanceAnalyzer()
        analyzer._config = _config(analysis_depth=1)

        with patch(
            "quality_agents.architectanalyst.metrics.distance_analyzer.DependencyGraphBuilder"
        ) as MockBuilder:
            MockBuilder.return_value.build.return_value = _mock_graph([])
            results = analyzer.analyze(tmp_path, [])

        assert results == []
