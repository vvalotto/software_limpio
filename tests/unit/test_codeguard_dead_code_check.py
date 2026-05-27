"""Tests unitarios para DeadCodeCheck."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quality_agents.codeguard.agent import Severity
from quality_agents.codeguard.checks.dead_code_check import DeadCodeCheck
from quality_agents.codeguard.config import ChecksConfig, CodeGuardConfig
from quality_agents.shared.verifiable import ExecutionContext


class TestDeadCodeCheckProperties:
    def test_name(self):
        assert DeadCodeCheck().name == "DeadCode"

    def test_category(self):
        assert DeadCodeCheck().category == "quality"

    def test_estimated_duration(self):
        assert DeadCodeCheck().estimated_duration == 1.5

    def test_priority(self):
        assert DeadCodeCheck().priority == 4


class TestDeadCodeCheckShouldRun:
    def _context(self, path="sample.py", excluded=False, config=None):
        ctx = MagicMock(spec=ExecutionContext)
        ctx.file_path = Path(path)
        ctx.is_excluded = excluded
        ctx.config = config
        return ctx

    def test_runs_on_python_file(self):
        assert DeadCodeCheck().should_run(self._context("sample.py")) is True

    def test_skips_non_python_file(self):
        assert DeadCodeCheck().should_run(self._context("sample.js")) is False

    def test_skips_excluded_file(self):
        assert DeadCodeCheck().should_run(self._context(excluded=True)) is False

    def test_skips_when_toggle_disabled(self):
        config = CodeGuardConfig(checks=ChecksConfig(dead_code=False))
        assert DeadCodeCheck().should_run(self._context(config=config)) is False

    def test_runs_when_toggle_enabled(self):
        config = CodeGuardConfig(checks=ChecksConfig(dead_code=True))
        assert DeadCodeCheck().should_run(self._context(config=config)) is True


class TestDeadCodeCheckParseOutput:
    def test_parses_unused_function(self):
        output = "sample.py:10: unused function 'my_func' (60% confidence)"
        findings = DeadCodeCheck()._parse_vulture_output(output)
        assert len(findings) == 1
        assert findings[0] == {"line": 10, "kind": "function", "name": "my_func", "confidence": 60}

    def test_parses_unused_class(self):
        output = "sample.py:5: unused class 'MyClass' (90% confidence)"
        findings = DeadCodeCheck()._parse_vulture_output(output)
        assert len(findings) == 1
        assert findings[0]["kind"] == "class"
        assert findings[0]["confidence"] == 90

    def test_parses_unused_variable(self):
        output = "sample.py:20: unused variable 'x' (60% confidence)"
        findings = DeadCodeCheck()._parse_vulture_output(output)
        assert findings[0]["kind"] == "variable"

    def test_parses_unused_import(self):
        output = "sample.py:1: unused import 'os' (100% confidence)"
        findings = DeadCodeCheck()._parse_vulture_output(output)
        assert findings[0]["name"] == "os"

    def test_parses_multiple_findings(self):
        output = (
            "sample.py:10: unused function 'foo' (60% confidence)\n"
            "sample.py:20: unused class 'Bar' (80% confidence)\n"
        )
        findings = DeadCodeCheck()._parse_vulture_output(output)
        assert len(findings) == 2

    def test_empty_output_returns_empty(self):
        assert DeadCodeCheck()._parse_vulture_output("") == []

    def test_ignores_non_matching_lines(self):
        output = "some random line\nanother line"
        assert DeadCodeCheck()._parse_vulture_output(output) == []


class TestDeadCodeCheckExecute:
    def test_returns_info_when_no_dead_code(self, tmp_path):
        f = tmp_path / "clean.py"
        f.write_text("def used(): pass\nused()\n")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", returncode=0)
            results = DeadCodeCheck().execute(f)
        assert len(results) == 1
        assert results[0].severity == Severity.INFO
        assert "No dead code" in results[0].message

    def test_returns_warning_for_low_confidence(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("def unused(): pass\n")
        output = f"{f}:1: unused function 'unused' (60% confidence)\n"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=output, returncode=1)
            results = DeadCodeCheck().execute(f)
        assert results[0].severity == Severity.WARNING
        assert "unused" in results[0].message
        assert results[0].line_number == 1

    def test_returns_error_for_high_confidence(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("def dead(): pass\n")
        output = f"{f}:1: unused function 'dead' (80% confidence)\n"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=output, returncode=1)
            results = DeadCodeCheck().execute(f)
        assert results[0].severity == Severity.ERROR

    def test_returns_error_when_vulture_not_installed(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        with patch("subprocess.run", side_effect=FileNotFoundError):
            results = DeadCodeCheck().execute(f)
        assert results[0].severity == Severity.ERROR
        assert "vulture not installed" in results[0].message

    def test_returns_error_on_timeout(self, tmp_path):
        import subprocess

        f = tmp_path / "sample.py"
        f.write_text("")
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("vulture", 10)):
            results = DeadCodeCheck().execute(f)
        assert results[0].severity == Severity.ERROR
        assert "timed out" in results[0].message

    def test_returns_error_on_unexpected_exception(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        with patch("subprocess.run", side_effect=RuntimeError("boom")):
            results = DeadCodeCheck().execute(f)
        assert results[0].severity == Severity.ERROR
        assert "boom" in results[0].message

    def test_confidence_boundary_79_is_warning(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        output = f"{f}:5: unused function 'f' (79% confidence)\n"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=output, returncode=1)
            results = DeadCodeCheck().execute(f)
        assert results[0].severity == Severity.WARNING

    def test_confidence_boundary_80_is_error(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        output = f"{f}:5: unused function 'f' (80% confidence)\n"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=output, returncode=1)
            results = DeadCodeCheck().execute(f)
        assert results[0].severity == Severity.ERROR
