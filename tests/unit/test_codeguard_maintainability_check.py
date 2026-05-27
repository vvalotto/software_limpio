"""Tests unitarios para MaintainabilityCheck."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quality_agents.codeguard.agent import Severity
from quality_agents.codeguard.checks.maintainability_check import MaintainabilityCheck
from quality_agents.codeguard.config import ChecksConfig, CodeGuardConfig
from quality_agents.shared.verifiable import ExecutionContext


class TestMaintainabilityCheckProperties:
    def test_name(self):
        assert MaintainabilityCheck().name == "Maintainability"

    def test_category(self):
        assert MaintainabilityCheck().category == "complexity"

    def test_estimated_duration(self):
        assert MaintainabilityCheck().estimated_duration == 1.0

    def test_priority(self):
        assert MaintainabilityCheck().priority == 4


class TestMaintainabilityCheckShouldRun:
    def _context(self, path="sample.py", excluded=False, config=None):
        ctx = MagicMock(spec=ExecutionContext)
        ctx.file_path = Path(path)
        ctx.is_excluded = excluded
        ctx.config = config
        return ctx

    def test_runs_on_python_file(self):
        assert MaintainabilityCheck().should_run(self._context("sample.py")) is True

    def test_skips_non_python_file(self):
        assert MaintainabilityCheck().should_run(self._context("sample.js")) is False

    def test_skips_excluded_file(self):
        assert MaintainabilityCheck().should_run(self._context(excluded=True)) is False

    def test_skips_when_toggle_disabled(self):
        config = CodeGuardConfig(checks=ChecksConfig(maintainability=False))
        assert MaintainabilityCheck().should_run(self._context(config=config)) is False

    def test_runs_when_toggle_enabled(self):
        config = CodeGuardConfig(checks=ChecksConfig(maintainability=True))
        assert MaintainabilityCheck().should_run(self._context(config=config)) is True


class TestMaintainabilityCheckParseOutput:
    def _json_output(self, path, mi, rank):
        return json.dumps({path: {"mi": mi, "rank": rank}})

    def test_parses_grade_a(self):
        output = self._json_output("sample.py", 69.72, "A")
        mi, rank = MaintainabilityCheck()._parse_radon_output(output, "sample.py")
        assert pytest.approx(mi, 0.01) == 69.72
        assert rank == "A"

    def test_parses_grade_b(self):
        output = self._json_output("sample.py", 15.0, "B")
        mi, rank = MaintainabilityCheck()._parse_radon_output(output, "sample.py")
        assert mi == 15.0
        assert rank == "B"

    def test_parses_grade_c(self):
        output = self._json_output("sample.py", 5.0, "C")
        mi, rank = MaintainabilityCheck()._parse_radon_output(output, "sample.py")
        assert mi == 5.0
        assert rank == "C"

    def test_empty_output_returns_none(self):
        mi, rank = MaintainabilityCheck()._parse_radon_output("", "sample.py")
        assert mi is None
        assert rank is None

    def test_invalid_json_returns_none(self):
        mi, rank = MaintainabilityCheck()._parse_radon_output("not json", "sample.py")
        assert mi is None

    def test_empty_json_object_returns_none(self):
        mi, rank = MaintainabilityCheck()._parse_radon_output("{}", "sample.py")
        assert mi is None


class TestMaintainabilityCheckExecute:
    def _mock_output(self, path, mi, rank):
        return json.dumps({str(path): {"mi": mi, "rank": rank}})

    def test_returns_info_when_mi_above_threshold(self, tmp_path):
        f = tmp_path / "clean.py"
        f.write_text("x = 1\n")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=self._mock_output(f, 70.0, "A"), returncode=0)
            results = MaintainabilityCheck().execute(f)
        assert results[0].severity == Severity.INFO
        assert "70.0" in results[0].message
        assert "A" in results[0].message

    def test_returns_warning_when_mi_between_10_and_threshold(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=self._mock_output(f, 15.0, "B"), returncode=0)
            results = MaintainabilityCheck().execute(f)
        assert results[0].severity == Severity.WARNING
        assert "15.0" in results[0].message

    def test_returns_error_when_mi_below_10(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=self._mock_output(f, 5.0, "C"), returncode=0)
            results = MaintainabilityCheck().execute(f)
        assert results[0].severity == Severity.ERROR
        assert "5.0" in results[0].message

    def test_returns_info_when_output_empty(self, tmp_path):
        f = tmp_path / "empty.py"
        f.write_text("")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", returncode=0)
            results = MaintainabilityCheck().execute(f)
        assert results[0].severity == Severity.INFO
        assert "could not be calculated" in results[0].message

    def test_returns_error_when_radon_not_installed(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        with patch("subprocess.run", side_effect=FileNotFoundError):
            results = MaintainabilityCheck().execute(f)
        assert results[0].severity == Severity.ERROR
        assert "radon not installed" in results[0].message

    def test_returns_error_on_timeout(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("radon", 10)):
            results = MaintainabilityCheck().execute(f)
        assert results[0].severity == Severity.ERROR
        assert "timed out" in results[0].message

    def test_returns_error_on_unexpected_exception(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        with patch("subprocess.run", side_effect=RuntimeError("boom")):
            results = MaintainabilityCheck().execute(f)
        assert results[0].severity == Severity.ERROR
        assert "boom" in results[0].message

    def test_mi_boundary_exactly_10_is_warning(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=self._mock_output(f, 10.0, "B"), returncode=0)
            results = MaintainabilityCheck().execute(f)
        assert results[0].severity == Severity.WARNING

    def test_mi_boundary_exactly_threshold_is_info(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=self._mock_output(f, 20.0, "A"), returncode=0)
            results = MaintainabilityCheck().execute(f)
        assert results[0].severity == Severity.INFO
