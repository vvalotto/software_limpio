"""
Tests unitarios para PEP8Check.

Fecha de creación: 2026-02-03
Ticket: 2.1
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from quality_agents.codeguard.agent import Severity
from quality_agents.codeguard.checks.pep8_check import PEP8Check
from quality_agents.codeguard.config import CodeGuardConfig
from quality_agents.shared.verifiable import ExecutionContext


class TestPEP8CheckProperties:
    """Tests para las propiedades de PEP8Check."""

    def test_name(self):
        check = PEP8Check()
        assert check.name == "PEP8"

    def test_category(self):
        check = PEP8Check()
        assert check.category == "style"

    def test_estimated_duration(self):
        check = PEP8Check()
        assert check.estimated_duration == 0.5

    def test_priority(self):
        check = PEP8Check()
        assert check.priority == 2


class TestPEP8CheckShouldRun:
    """Tests para el método should_run()."""

    def test_should_run_on_python_file(self):
        check = PEP8Check()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(check_pep8=True),
        )
        assert check.should_run(context) is True

    def test_should_not_run_on_excluded_file(self):
        check = PEP8Check()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=True,
            config=CodeGuardConfig(check_pep8=True),
        )
        assert check.should_run(context) is False

    def test_should_not_run_on_non_python_file(self):
        check = PEP8Check()
        context = ExecutionContext(
            file_path=Path("test.txt"),
            is_excluded=False,
            config=CodeGuardConfig(check_pep8=True),
        )
        assert check.should_run(context) is False

    def test_should_not_run_when_disabled_in_config(self):
        check = PEP8Check()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(check_pep8=False),
        )
        assert check.should_run(context) is False

    def test_should_run_when_config_is_none(self):
        # Si no hay config, asumir que está habilitado
        check = PEP8Check()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=None,
        )
        assert check.should_run(context) is True


class TestPEP8CheckExecute:
    """Tests para el método execute()."""

    @patch("subprocess.run")
    def test_execute_with_no_errors(self, mock_run):
        # Mock de flake8 sin errores
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
        )

        check = PEP8Check()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "PEP8"
        assert results[0].severity == Severity.INFO
        assert "PEP8 compliant" in results[0].message
        assert results[0].file_path == "test.py"

    @patch("subprocess.run")
    def test_execute_with_pep8_violations(self, mock_run):
        # Mock de flake8 con errores
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="test.py:10:5: E501 line too long (101 > 100 characters)\ntest.py:15:1: E302 expected 2 blank lines, found 1",
            stderr="",
        )

        check = PEP8Check()
        results = check.execute(Path("test.py"))

        assert len(results) == 2

        # Primer error
        assert results[0].check_name == "PEP8"
        assert results[0].severity == Severity.WARNING
        assert "E501" in results[0].message
        assert results[0].file_path == "test.py"
        assert results[0].line_number == 10

        # Segundo error
        assert results[1].check_name == "PEP8"
        assert results[1].severity == Severity.WARNING
        assert "E302" in results[1].message
        assert results[1].file_path == "test.py"
        assert results[1].line_number == 15

    @patch("subprocess.run")
    def test_execute_with_flake8_not_installed(self, mock_run):
        # Mock de FileNotFoundError (flake8 no instalado)
        mock_run.side_effect = FileNotFoundError()

        check = PEP8Check()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "PEP8"
        assert results[0].severity == Severity.ERROR
        assert "not installed" in results[0].message

    @patch("subprocess.run")
    def test_execute_with_timeout(self, mock_run):
        # Mock de TimeoutExpired
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="flake8", timeout=5)

        check = PEP8Check()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "PEP8"
        assert results[0].severity == Severity.ERROR
        assert "timed out" in results[0].message

    @patch("subprocess.run")
    def test_execute_with_unexpected_error(self, mock_run):
        # Mock de error inesperado
        mock_run.side_effect = RuntimeError("Unexpected error")

        check = PEP8Check()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "PEP8"
        assert results[0].severity == Severity.ERROR
        assert "Unexpected error" in results[0].message

    @patch("subprocess.run")
    def test_execute_calls_flake8_with_correct_args(self, mock_run):
        # Verificar que se llama flake8 con los argumentos correctos
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        check = PEP8Check()
        check.execute(Path("/tmp/test.py"))

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "flake8"
        assert "--max-line-length=100" in args
        assert "/tmp/test.py" in args
