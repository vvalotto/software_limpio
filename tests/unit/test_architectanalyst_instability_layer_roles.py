"""Tests unitarios para layer_roles en InstabilityAnalyzer (#47)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quality_agents.architectanalyst.config import ArchitectAnalystConfig
from quality_agents.architectanalyst.metrics.instability_analyzer import InstabilityAnalyzer
from quality_agents.architectanalyst.models import ArchitectureSeverity


def _config(max_instability=0.8, layer_roles=None):
    cfg = ArchitectAnalystConfig(max_instability=max_instability)
    cfg.layer_roles = layer_roles or {}
    return cfg


def _mock_graph(modules_data):
    """
    modules_data: {module_name: (ca, ce)}
    """
    graph = MagicMock()
    graph.modules = list(modules_data.keys())
    graph.afferent_coupling.side_effect = lambda m: list(range(modules_data[m][0]))
    graph.efferent_coupling.side_effect = lambda m: list(range(modules_data[m][1]))
    return graph


class TestResolveRole:
    def test_no_roles_returns_none(self):
        a = InstabilityAnalyzer()
        assert a._resolve_role("myapp.domain.model", {}) is None

    def test_matches_glob_pattern(self):
        a = InstabilityAnalyzer()
        roles = {"*/domain/*": "stable"}
        assert a._resolve_role("myapp.domain.model", roles) == "stable"

    def test_matches_leaf_role(self):
        a = InstabilityAnalyzer()
        roles = {"*/commands/*": "leaf"}
        assert a._resolve_role("myapp.application.commands.create", roles) == "leaf"

    def test_no_match_returns_none(self):
        a = InstabilityAnalyzer()
        roles = {"*/domain/*": "stable"}
        assert a._resolve_role("myapp.infrastructure.db", roles) is None

    def test_invalid_role_ignored(self):
        a = InstabilityAnalyzer()
        roles = {"*/domain/*": "unknown_role"}
        assert a._resolve_role("myapp.domain.model", roles) is None

    def test_dots_converted_to_slashes_for_matching(self):
        a = InstabilityAnalyzer()
        roles = {"myapp/domain/*": "stable"}
        assert a._resolve_role("myapp.domain.model", roles) == "stable"


class TestEvaluarModulo:
    def test_no_role_warns_when_above_threshold(self):
        a = InstabilityAnalyzer()
        result = a._evaluar_modulo("myapp.foo", 0.9, ca=0, ce=5, threshold=0.8, role=None)
        assert result is not None
        assert result.severity == ArchitectureSeverity.WARNING

    def test_no_role_no_result_when_below_threshold(self):
        a = InstabilityAnalyzer()
        result = a._evaluar_modulo("myapp.foo", 0.5, ca=3, ce=2, threshold=0.8, role=None)
        assert result is None

    def test_stable_role_same_as_no_role(self):
        a = InstabilityAnalyzer()
        result = a._evaluar_modulo("myapp.foo", 0.9, ca=0, ce=5, threshold=0.8, role="stable")
        assert result is not None
        assert "rol: stable" in result.message

    def test_leaf_warns_when_i_too_low(self):
        a = InstabilityAnalyzer()
        # leaf threshold = 1.0 - 0.8 = 0.2
        # I=0.1 < 0.2 → warning
        result = a._evaluar_modulo("myapp.cmds.create", 0.1, ca=5, ce=0, threshold=0.8, role="leaf")
        assert result is not None
        assert result.severity == ArchitectureSeverity.WARNING
        assert "Leaf module" in result.message

    def test_leaf_no_result_when_i_is_high(self):
        a = InstabilityAnalyzer()
        # leaf threshold = 0.2; I=0.9 > 0.2 → no violation for leaf
        result = a._evaluar_modulo("myapp.cmds.create", 0.9, ca=0, ce=5, threshold=0.8, role="leaf")
        assert result is None

    def test_leaf_threshold_boundary(self):
        a = InstabilityAnalyzer()
        # leaf threshold = 0.2; I=0.2 exactly → no violation (not strictly less)
        result = a._evaluar_modulo("myapp.cmds", 0.2, ca=2, ce=8, threshold=0.8, role="leaf")
        assert result is None


class TestInstabilityAnalyzerWithLayerRoles:
    def test_analyze_without_layer_roles_unchanged(self, tmp_path):
        analyzer = InstabilityAnalyzer()
        analyzer._config = _config()

        with patch(
            "quality_agents.architectanalyst.metrics.instability_analyzer.DependencyGraphBuilder"
        ) as MockBuilder:
            MockBuilder.return_value.build.return_value = _mock_graph({
                "myapp.foo": (0, 5),  # I=1.0 > 0.8 → warning
                "myapp.bar": (3, 1),  # I=0.25 < 0.8 → no warning
            })
            results = analyzer.analyze(tmp_path, [])

        assert len(results) == 1
        assert results[0].value == 1.0

    def test_analyze_leaf_module_warns_when_too_stable(self, tmp_path):
        analyzer = InstabilityAnalyzer()
        analyzer._config = _config(layer_roles={"myapp/commands/*": "leaf"})

        with patch(
            "quality_agents.architectanalyst.metrics.instability_analyzer.DependencyGraphBuilder"
        ) as MockBuilder:
            MockBuilder.return_value.build.return_value = _mock_graph({
                "myapp.commands.create": (5, 0),  # I=0.0 < 0.2 → leaf warning
            })
            results = analyzer.analyze(tmp_path, [])

        assert len(results) == 1
        assert "Leaf module" in results[0].message

    def test_analyze_leaf_module_no_warning_when_unstable(self, tmp_path):
        analyzer = InstabilityAnalyzer()
        analyzer._config = _config(layer_roles={"myapp/commands/*": "leaf"})

        with patch(
            "quality_agents.architectanalyst.metrics.instability_analyzer.DependencyGraphBuilder"
        ) as MockBuilder:
            MockBuilder.return_value.build.return_value = _mock_graph({
                "myapp.commands.create": (0, 5),  # I=1.0 → leaf OK
            })
            results = analyzer.analyze(tmp_path, [])

        assert results == []

    def test_analyze_isolated_modules_skipped(self, tmp_path):
        analyzer = InstabilityAnalyzer()
        analyzer._config = _config()

        with patch(
            "quality_agents.architectanalyst.metrics.instability_analyzer.DependencyGraphBuilder"
        ) as MockBuilder:
            MockBuilder.return_value.build.return_value = _mock_graph({
                "myapp.isolated": (0, 0),
            })
            results = analyzer.analyze(tmp_path, [])

        assert results == []


class TestLayerRolesConfig:
    def test_default_layer_roles_is_empty(self):
        config = ArchitectAnalystConfig()
        assert config.layer_roles == {}

    def test_layer_roles_can_be_set(self):
        config = ArchitectAnalystConfig()
        config.layer_roles = {"*/domain/*": "stable", "*/commands/*": "leaf"}
        assert config.layer_roles["*/domain/*"] == "stable"

    def test_from_pyproject_toml_loads_layer_roles(self, tmp_path):
        toml = tmp_path / "pyproject.toml"
        toml.write_text(
            "[tool.architectanalyst]\n"
            "[tool.architectanalyst.layer_roles]\n"
            '"*/domain/*" = "stable"\n'
            '"*/commands/*" = "leaf"\n'
        )
        from quality_agents.architectanalyst.config import ArchitectAnalystConfig as Cfg
        config = Cfg.from_pyproject_toml(toml)
        assert config.layer_roles["*/domain/*"] == "stable"
        assert config.layer_roles["*/commands/*"] == "leaf"
