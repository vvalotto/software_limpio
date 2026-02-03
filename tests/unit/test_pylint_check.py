"""
Tests unitarios para PylintCheck.

Fecha de creación: 2026-02-03
Ticket: 2.2
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quality_agents.codeguard.agent import CheckResult, Severity
from quality_agents.codeguard.checks.pylint_check import PylintCheck
from quality_agents.codeguard.config import CodeGuardConfig
from quality_agents.shared.verifiable import ExecutionContext


class TestPylintCheckProperties:
    """Tests para las propiedades de PylintCheck."""

    def test_name(self):
        check = PylintCheck()
        assert check.name == "Pylint"

    def test_category(self):
        check = PylintCheck()
        assert check.category == "quality"

    def test_estimated_duration(self):
        check = PylintCheck()
        assert check.estimated_duration == 2.0

    def test_priority(self):
        check = PylintCheck()
        assert check.priority == 4


class TestPylintCheckShouldRun:
    """Tests para el método should_run()."""

    def test_should_run_on_python_file(self):
        check = PylintCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(check_pylint=True),
        )
        assert check.should_run(context) is True

    def test_should_not_run_on_excluded_file(self):
        check = PylintCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=True,
            config=CodeGuardConfig(check_pylint=True),
        )
        assert check.should_run(context) is False

    def test_should_not_run_on_non_python_file(self):
        check = PylintCheck()
        context = ExecutionContext(
            file_path=Path("test.txt"),
            is_excluded=False,
            config=CodeGuardConfig(check_pylint=True),
        )
        assert check.should_run(context) is False

    def test_should_not_run_when_disabled_in_config(self):
        check = PylintCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(check_pylint=False),
        )
        assert check.should_run(context) is False

    def test_should_run_when_config_is_none(self):
        # Si no hay config, asumir que está habilitado
        check = PylintCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=None,
        )
        assert check.should_run(context) is True


class TestPylintCheckExecute:
    """Tests para el método execute()."""

    @patch("subprocess.run")
    def test_execute_with_high_score(self, mock_run):
        # Mock de pylint con score alto (>= 8.0)
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Your code has been rated at 9.50/10",
            stderr="",
        )

        check = PylintCheck()
        check._context = ExecutionContext(
            file_path=Path("test.py"),
            config=CodeGuardConfig(min_pylint_score=8.0),
        )
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Pylint"
        assert results[0].severity == Severity.INFO
        assert "9.50/10" in results[0].message
        assert ">= 8.0" in results[0].message

    @patch("subprocess.run")
    def test_execute_with_low_score(self, mock_run):
        # Mock de pylint con score bajo (< 8.0)
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="Your code has been rated at 6.25/10",
            stderr="",
        )

        check = PylintCheck()
        check._context = ExecutionContext(
            file_path=Path("test.py"),
            config=CodeGuardConfig(min_pylint_score=8.0),
        )
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Pylint"
        assert results[0].severity == Severity.WARNING
        assert "6.25/10" in results[0].message
        assert "< 8.0" in results[0].message

    @patch("subprocess.run")
    def test_execute_with_perfect_score(self, mock_run):
        # Mock de pylint con score perfecto (10/10)
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Your code has been rated at 10.00/10",
            stderr="",
        )

        check = PylintCheck()
        check._context = ExecutionContext(
            file_path=Path("test.py"),
            config=CodeGuardConfig(min_pylint_score=8.0),
        )
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].severity == Severity.INFO
        assert "10.00/10" in results[0].message

    @patch("subprocess.run")
    def test_execute_with_custom_min_score(self, mock_run):
        # Mock de pylint con score 7.5, min_score 7.0
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Your code has been rated at 7.50/10",
            stderr="",
        )

        check = PylintCheck()
        check._context = ExecutionContext(
            file_path=Path("test.py"),
            config=CodeGuardConfig(min_pylint_score=7.0),
        )
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].severity == Severity.INFO
        assert "7.50/10" in results[0].message
        assert ">= 7.0" in results[0].message

    @patch("subprocess.run")
    def test_execute_with_pylint_not_installed(self, mock_run):
        # Mock de FileNotFoundError (pylint no instalado)
        mock_run.side_effect = FileNotFoundError()

        check = PylintCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Pylint"
        assert results[0].severity == Severity.ERROR
        assert "not installed" in results[0].message

    @patch("subprocess.run")
    def test_execute_with_timeout(self, mock_run):
        # Mock de TimeoutExpired
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="pylint", timeout=10)

        check = PylintCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Pylint"
        assert results[0].severity == Severity.ERROR
        assert "timed out" in results[0].message

    @patch("subprocess.run")
    def test_execute_with_unexpected_error(self, mock_run):
        # Mock de error inesperado
        mock_run.side_effect = RuntimeError("Unexpected error")

        check = PylintCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Pylint"
        assert results[0].severity == Severity.ERROR
        assert "Unexpected error" in results[0].message

    @patch("subprocess.run")
    def test_execute_with_no_score_in_output(self, mock_run):
        # Mock de pylint sin score en output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Some output without score",
            stderr="",
        )

        check = PylintCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].severity == Severity.ERROR
        assert "Could not extract" in results[0].message

    @patch("subprocess.run")
    def test_execute_calls_pylint_with_correct_args(self, mock_run):
        # Verificar que se llama pylint con los argumentos correctos
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Your code has been rated at 8.00/10",
            stderr="",
        )

        check = PylintCheck()
        check._context = ExecutionContext(
            file_path=Path("test.py"),
            config=CodeGuardConfig(),
        )
        check.execute(Path("/tmp/test.py"))

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "pylint"
        assert "--score=y" in args
        assert "/tmp/test.py" in args


class TestPylintCheckExtractScore:
    """Tests para el método _extract_score()."""

    def test_extract_score_standard_format(self):
        check = PylintCheck()
        output = "Your code has been rated at 9.50/10"
        score = check._extract_score(output)
        assert score == 9.50

    def test_extract_score_with_previous_run(self):
        check = PylintCheck()
        output = "Your code has been rated at 8.25/10 (previous run: 7.50/10)"
        score = check._extract_score(output)
        assert score == 8.25

    def test_extract_score_integer_value(self):
        check = PylintCheck()
        output = "Your code has been rated at 10/10"
        score = check._extract_score(output)
        assert score == 10.0

    def test_extract_score_no_match(self):
        check = PylintCheck()
        output = "Some random output without score"
        score = check._extract_score(output)
        assert score is None

    def test_extract_score_empty_string(self):
        check = PylintCheck()
        score = check._extract_score("")
        assert score is None
