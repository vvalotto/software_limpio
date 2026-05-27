"""Tests unitarios para LawOfDemeterAnalyzer."""

import textwrap
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from quality_agents.designreviewer.analyzers.law_of_demeter_analyzer import LawOfDemeterAnalyzer
from quality_agents.designreviewer.config import DesignReviewerChecksConfig, DesignReviewerConfig
from quality_agents.designreviewer.models import ReviewSeverity
from quality_agents.shared.verifiable import ExecutionContext


def _write(tmp_path: Path, code: str) -> Path:
    f = tmp_path / "sample.py"
    f.write_text(textwrap.dedent(code))
    return f


def _context(config=None, excluded=False, path="sample.py"):
    ctx = MagicMock(spec=ExecutionContext)
    ctx.file_path = Path(path)
    ctx.is_excluded = excluded
    ctx.config = config
    return ctx


class TestLawOfDemeterAnalyzerProperties:
    def test_name(self):
        assert LawOfDemeterAnalyzer().name == "LawOfDemeterAnalyzer"

    def test_category(self):
        assert LawOfDemeterAnalyzer().category == "smells"

    def test_priority(self):
        assert LawOfDemeterAnalyzer().priority == 4

    def test_estimated_duration(self):
        assert LawOfDemeterAnalyzer().estimated_duration == 0.8


class TestLawOfDemeterAnalyzerShouldRun:
    def test_runs_on_python_file(self):
        assert LawOfDemeterAnalyzer().should_run(_context()) is True

    def test_skips_non_python_file(self):
        assert LawOfDemeterAnalyzer().should_run(_context(path="sample.js")) is False

    def test_skips_excluded(self):
        assert LawOfDemeterAnalyzer().should_run(_context(excluded=True)) is False

    def test_skips_when_toggle_disabled(self):
        config = DesignReviewerConfig(checks=DesignReviewerChecksConfig(law_of_demeter=False))
        assert LawOfDemeterAnalyzer().should_run(_context(config=config)) is False

    def test_runs_when_toggle_enabled(self):
        config = DesignReviewerConfig(checks=DesignReviewerChecksConfig(law_of_demeter=True))
        assert LawOfDemeterAnalyzer().should_run(_context(config=config)) is True


class TestLawOfDemeterAnalyzerExecute:
    def test_no_violation_depth_1(self, tmp_path):
        code = """
            def get_city(order):
                return order.city
        """
        f = _write(tmp_path, code)
        analyzer = LawOfDemeterAnalyzer()
        analyzer._config = DesignReviewerConfig()
        results = analyzer.execute(f)
        assert results == []

    def test_violation_depth_2(self, tmp_path):
        code = """
            def get_city(order):
                return order.address.city
        """
        f = _write(tmp_path, code)
        analyzer = LawOfDemeterAnalyzer()
        analyzer._config = DesignReviewerConfig()
        results = analyzer.execute(f)
        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.WARNING
        assert "order.address.city" in results[0].message

    def test_violation_depth_3(self, tmp_path):
        code = """
            def get_city(order):
                return order.customer.address.city
        """
        f = _write(tmp_path, code)
        analyzer = LawOfDemeterAnalyzer()
        analyzer._config = DesignReviewerConfig()
        results = analyzer.execute(f)
        assert len(results) == 1
        assert results[0].current_value == 3

    def test_self_chain_excluded(self, tmp_path):
        code = """
            class Foo:
                def bar(self):
                    return self.address.city
        """
        f = _write(tmp_path, code)
        analyzer = LawOfDemeterAnalyzer()
        analyzer._config = DesignReviewerConfig()
        results = analyzer.execute(f)
        assert results == []

    def test_custom_depth_threshold(self, tmp_path):
        code = """
            def get(obj):
                return obj.a.b
        """
        f = _write(tmp_path, code)
        analyzer = LawOfDemeterAnalyzer()
        analyzer._config = DesignReviewerConfig(max_demeter_depth=2)
        results = analyzer.execute(f)
        assert results == []

    def test_multiple_violations_in_one_function(self, tmp_path):
        code = """
            def process(order):
                city = order.address.city
                name = order.customer.profile.name
        """
        f = _write(tmp_path, code)
        analyzer = LawOfDemeterAnalyzer()
        analyzer._config = DesignReviewerConfig()
        results = analyzer.execute(f)
        assert len(results) == 2

    def test_violation_reports_function_name(self, tmp_path):
        code = """
            def get_city(order):
                return order.address.city
        """
        f = _write(tmp_path, code)
        analyzer = LawOfDemeterAnalyzer()
        analyzer._config = DesignReviewerConfig()
        results = analyzer.execute(f)
        assert results[0].class_name == "get_city"

    def test_violation_has_suggestion(self, tmp_path):
        code = """
            def get_city(order):
                return order.address.city
        """
        f = _write(tmp_path, code)
        analyzer = LawOfDemeterAnalyzer()
        analyzer._config = DesignReviewerConfig()
        results = analyzer.execute(f)
        assert results[0].suggestion is not None

    def test_empty_file_returns_empty(self, tmp_path):
        f = _write(tmp_path, "")
        analyzer = LawOfDemeterAnalyzer()
        analyzer._config = DesignReviewerConfig()
        assert analyzer.execute(f) == []

    def test_syntax_error_returns_empty(self, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text("def broken(:")
        analyzer = LawOfDemeterAnalyzer()
        analyzer._config = DesignReviewerConfig()
        assert analyzer.execute(f) == []

    def test_threshold_in_message(self, tmp_path):
        code = """
            def get(obj):
                return obj.a.b
        """
        f = _write(tmp_path, code)
        analyzer = LawOfDemeterAnalyzer()
        analyzer._config = DesignReviewerConfig(max_demeter_depth=1)
        results = analyzer.execute(f)
        assert "máx 1" in results[0].message

    def test_violation_depth_exactly_at_threshold_plus_1(self, tmp_path):
        code = """
            def get(obj):
                return obj.a.b
        """
        f = _write(tmp_path, code)
        analyzer = LawOfDemeterAnalyzer()
        analyzer._config = DesignReviewerConfig(max_demeter_depth=1)
        results = analyzer.execute(f)
        assert results[0].current_value == 2
        assert results[0].threshold == 1
