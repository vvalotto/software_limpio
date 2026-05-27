"""Tests unitarios para SpellingCheck."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quality_agents.codeguard.agent import Severity
from quality_agents.codeguard.checks.spelling_check import SpellingCheck
from quality_agents.codeguard.config import ChecksConfig, CodeGuardConfig
from quality_agents.shared.verifiable import ExecutionContext


class TestSpellingCheckProperties:
    def test_name(self):
        assert SpellingCheck().name == "Spelling"

    def test_category(self):
        assert SpellingCheck().category == "style"

    def test_estimated_duration(self):
        assert SpellingCheck().estimated_duration == 1.0

    def test_priority(self):
        assert SpellingCheck().priority == 5


class TestSpellingCheckShouldRun:
    def _context(self, path="sample.py", excluded=False, config=None):
        ctx = MagicMock(spec=ExecutionContext)
        ctx.file_path = Path(path)
        ctx.is_excluded = excluded
        ctx.config = config
        return ctx

    def test_runs_on_python_file(self):
        assert SpellingCheck().should_run(self._context("sample.py")) is True

    def test_skips_non_python_file(self):
        assert SpellingCheck().should_run(self._context("sample.js")) is False

    def test_skips_excluded_file(self):
        assert SpellingCheck().should_run(self._context(excluded=True)) is False

    def test_skips_when_toggle_disabled(self):
        config = CodeGuardConfig(checks=ChecksConfig(spelling=False))
        assert SpellingCheck().should_run(self._context(config=config)) is False

    def test_runs_when_toggle_enabled(self):
        config = CodeGuardConfig(checks=ChecksConfig(spelling=True))
        assert SpellingCheck().should_run(self._context(config=config)) is True


class TestSpellingCheckParseOutput:
    def test_parses_single_typo(self):
        output = "sample.py:10: calcualte ==> calculate"
        findings = SpellingCheck()._parse_codespell_output(output)
        assert len(findings) == 1
        assert findings[0] == {"line": 10, "typo": "calcualte", "correction": "calculate"}

    def test_parses_multiple_typos(self):
        output = (
            "sample.py:1: amout ==> amount\n"
            "sample.py:5: teh ==> the\n"
        )
        findings = SpellingCheck()._parse_codespell_output(output)
        assert len(findings) == 2
        assert findings[0]["typo"] == "amout"
        assert findings[1]["typo"] == "teh"

    def test_empty_output_returns_empty(self):
        assert SpellingCheck()._parse_codespell_output("") == []

    def test_ignores_non_matching_lines(self):
        output = "some random line\nno match here"
        assert SpellingCheck()._parse_codespell_output(output) == []

    def test_parses_line_number_correctly(self):
        output = "path/to/file.py:42: exampl ==> example"
        findings = SpellingCheck()._parse_codespell_output(output)
        assert findings[0]["line"] == 42


class TestSpellingCheckExecute:
    def test_returns_info_when_no_typos(self, tmp_path):
        f = tmp_path / "clean.py"
        f.write_text("def calculate_total(amount): return amount\n")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
            results = SpellingCheck().execute(f)
        assert len(results) == 1
        assert results[0].severity == Severity.INFO
        assert "No spelling errors" in results[0].message

    def test_returns_warning_for_each_typo(self, tmp_path):
        f = tmp_path / "typos.py"
        f.write_text("")
        output = (
            f"{f}:1: calcualte ==> calculate\n"
            f"{f}:3: amout ==> amount\n"
        )
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=output, stderr="", returncode=65)
            results = SpellingCheck().execute(f)
        assert len(results) == 2
        assert all(r.severity == Severity.WARNING for r in results)
        assert results[0].line_number == 1
        assert results[1].line_number == 3

    def test_warning_message_includes_typo_and_correction(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        output = f"{f}:5: teh ==> the\n"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=output, stderr="", returncode=65)
            results = SpellingCheck().execute(f)
        assert "'teh'" in results[0].message
        assert "'the'" in results[0].message

    def test_returns_error_when_codespell_not_installed(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        with patch("subprocess.run", side_effect=FileNotFoundError):
            results = SpellingCheck().execute(f)
        assert results[0].severity == Severity.ERROR
        assert "codespell not installed" in results[0].message

    def test_returns_error_on_timeout(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("codespell", 10)):
            results = SpellingCheck().execute(f)
        assert results[0].severity == Severity.ERROR
        assert "timed out" in results[0].message

    def test_returns_error_on_unexpected_exception(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        with patch("subprocess.run", side_effect=RuntimeError("boom")):
            results = SpellingCheck().execute(f)
        assert results[0].severity == Severity.ERROR
        assert "boom" in results[0].message

    def test_parses_output_from_stderr(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("")
        stderr_output = f"{f}:2: recieve ==> receive\n"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", stderr=stderr_output, returncode=65)
            results = SpellingCheck().execute(f)
        assert len(results) == 1
        assert results[0].severity == Severity.WARNING
