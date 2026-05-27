"""Tests unitarios para CoverageAnalyzer (#49)."""

import json
from pathlib import Path

import pytest

from quality_agents.architectanalyst.config import (
    ArchitectAnalystChecksConfig,
    ArchitectAnalystConfig,
)
from quality_agents.architectanalyst.metrics.coverage_analyzer import CoverageAnalyzer
from quality_agents.architectanalyst.models import ArchitectureSeverity


def _config(min_coverage=80.0, report_path="coverage.json", enabled=True):
    return ArchitectAnalystConfig(
        min_coverage=min_coverage,
        coverage_report_path=report_path,
        checks=ArchitectAnalystChecksConfig(coverage=enabled),
    )


def _write_coverage_json(path: Path, percent: float) -> Path:
    data = {
        "meta": {"version": "7.0.0"},
        "files": {},
        "totals": {
            "covered_lines": 100,
            "num_statements": 100,
            "percent_covered": percent,
            "percent_covered_display": str(int(percent)),
        },
    }
    coverage_file = path / "coverage.json"
    coverage_file.write_text(json.dumps(data), encoding="utf-8")
    return coverage_file


class TestCoverageAnalyzerProperties:
    def test_name(self):
        assert CoverageAnalyzer().name == "CoverageAnalyzer"

    def test_category(self):
        assert CoverageAnalyzer().category == "quality"

    def test_priority(self):
        assert CoverageAnalyzer().priority == 11

    def test_estimated_duration(self):
        assert CoverageAnalyzer().estimated_duration == 1.0


class TestCoverageShouldRun:
    def test_runs_by_default(self):
        a = CoverageAnalyzer()
        assert a.should_run(_config()) is True

    def test_skips_when_toggle_disabled(self):
        a = CoverageAnalyzer()
        assert a.should_run(_config(enabled=False)) is False

    def test_runs_when_toggle_enabled(self):
        a = CoverageAnalyzer()
        assert a.should_run(_config(enabled=True)) is True


class TestCoverageFileNotFound:
    def test_warning_when_file_absent(self, tmp_path):
        a = CoverageAnalyzer()
        a._config = _config()
        results = a.analyze(tmp_path, [])

        assert len(results) == 1
        assert results[0].severity == ArchitectureSeverity.WARNING
        assert results[0].metric_name == "coverage"

    def test_message_mentions_pytest_command(self, tmp_path):
        a = CoverageAnalyzer()
        a._config = _config()
        results = a.analyze(tmp_path, [])

        assert "pytest" in results[0].message

    def test_custom_path_mentioned_in_message(self, tmp_path):
        a = CoverageAnalyzer()
        a._config = _config(report_path="reports/cov.json")
        results = a.analyze(tmp_path, [])

        assert "reports/cov.json" in results[0].message


class TestCoverageInvalidFile:
    def test_warning_on_invalid_json(self, tmp_path):
        bad_file = tmp_path / "coverage.json"
        bad_file.write_text("not json", encoding="utf-8")

        a = CoverageAnalyzer()
        a._config = _config()
        results = a.analyze(tmp_path, [])

        assert len(results) == 1
        assert results[0].severity == ArchitectureSeverity.WARNING

    def test_warning_when_totals_key_missing(self, tmp_path):
        bad_file = tmp_path / "coverage.json"
        bad_file.write_text(json.dumps({"meta": {}}), encoding="utf-8")

        a = CoverageAnalyzer()
        a._config = _config()
        results = a.analyze(tmp_path, [])

        assert results[0].severity == ArchitectureSeverity.WARNING


class TestCoverageResults:
    def test_info_when_coverage_above_threshold(self, tmp_path):
        _write_coverage_json(tmp_path, percent=90.0)
        a = CoverageAnalyzer()
        a._config = _config(min_coverage=80.0)
        results = a.analyze(tmp_path, [])

        assert len(results) == 1
        assert results[0].severity == ArchitectureSeverity.INFO
        assert results[0].value == pytest.approx(90.0, abs=0.1)

    def test_warning_when_coverage_below_threshold(self, tmp_path):
        _write_coverage_json(tmp_path, percent=65.0)
        a = CoverageAnalyzer()
        a._config = _config(min_coverage=80.0)
        results = a.analyze(tmp_path, [])

        assert len(results) == 1
        assert results[0].severity == ArchitectureSeverity.WARNING
        assert results[0].value == pytest.approx(65.0, abs=0.1)

    def test_info_when_coverage_exactly_at_threshold(self, tmp_path):
        _write_coverage_json(tmp_path, percent=80.0)
        a = CoverageAnalyzer()
        a._config = _config(min_coverage=80.0)
        results = a.analyze(tmp_path, [])

        assert results[0].severity == ArchitectureSeverity.INFO

    def test_message_contains_percentage(self, tmp_path):
        _write_coverage_json(tmp_path, percent=75.5)
        a = CoverageAnalyzer()
        a._config = _config(min_coverage=80.0)
        results = a.analyze(tmp_path, [])

        assert "75.5" in results[0].message

    def test_threshold_in_result(self, tmp_path):
        _write_coverage_json(tmp_path, percent=70.0)
        a = CoverageAnalyzer()
        a._config = _config(min_coverage=85.0)
        results = a.analyze(tmp_path, [])

        assert results[0].threshold == pytest.approx(85.0)

    def test_custom_report_path(self, tmp_path):
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()
        data = {"totals": {"percent_covered": 92.0}}
        (reports_dir / "cov.json").write_text(json.dumps(data), encoding="utf-8")

        a = CoverageAnalyzer()
        a._config = _config(report_path="reports/cov.json")
        results = a.analyze(tmp_path, [])

        assert results[0].severity == ArchitectureSeverity.INFO
        assert results[0].value == pytest.approx(92.0, abs=0.1)


class TestCoverageConfig:
    def test_default_min_coverage(self):
        assert ArchitectAnalystConfig().min_coverage == 80.0

    def test_default_report_path(self):
        assert ArchitectAnalystConfig().coverage_report_path == "coverage.json"

    def test_default_toggle_enabled(self):
        assert ArchitectAnalystConfig().checks.coverage is True

    def test_from_pyproject_toml_loads_min_coverage(self, tmp_path):
        toml = tmp_path / "pyproject.toml"
        toml.write_text(
            "[tool.architectanalyst]\n"
            "min_coverage = 90.0\n"
        )
        config = ArchitectAnalystConfig.from_pyproject_toml(toml)
        assert config.min_coverage == 90.0

    def test_from_pyproject_toml_loads_report_path(self, tmp_path):
        toml = tmp_path / "pyproject.toml"
        toml.write_text(
            "[tool.architectanalyst]\n"
            'coverage_report_path = "reports/coverage.json"\n'
        )
        config = ArchitectAnalystConfig.from_pyproject_toml(toml)
        assert config.coverage_report_path == "reports/coverage.json"
