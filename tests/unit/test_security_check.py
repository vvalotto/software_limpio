"""
Tests unitarios para SecurityCheck.

Fecha de creación: 2026-02-03
Ticket: 2.3
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from quality_agents.codeguard.agent import Severity
from quality_agents.codeguard.checks.security_check import SecurityCheck
from quality_agents.codeguard.config import CodeGuardConfig
from quality_agents.shared.verifiable import ExecutionContext


class TestSecurityCheckProperties:
    """Tests para las propiedades de SecurityCheck."""

    def test_name(self):
        check = SecurityCheck()
        assert check.name == "Security"

    def test_category(self):
        check = SecurityCheck()
        assert check.category == "security"

    def test_estimated_duration(self):
        check = SecurityCheck()
        assert check.estimated_duration == 1.5

    def test_priority(self):
        check = SecurityCheck()
        assert check.priority == 1  # Máxima prioridad


class TestSecurityCheckShouldRun:
    """Tests para el método should_run()."""

    def test_should_run_on_python_file(self):
        check = SecurityCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(check_security=True),
        )
        assert check.should_run(context) is True

    def test_should_not_run_on_excluded_file(self):
        check = SecurityCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=True,
            config=CodeGuardConfig(check_security=True),
        )
        assert check.should_run(context) is False

    def test_should_not_run_on_non_python_file(self):
        check = SecurityCheck()
        context = ExecutionContext(
            file_path=Path("test.txt"),
            is_excluded=False,
            config=CodeGuardConfig(check_security=True),
        )
        assert check.should_run(context) is False

    def test_should_not_run_when_disabled_in_config(self):
        check = SecurityCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(check_security=False),
        )
        assert check.should_run(context) is False

    def test_should_run_when_config_is_none(self):
        # Si no hay config, asumir que está habilitado
        check = SecurityCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=None,
        )
        assert check.should_run(context) is True


class TestSecurityCheckExecute:
    """Tests para el método execute()."""

    @patch("subprocess.run")
    def test_execute_with_no_issues(self, mock_run):
        # Mock de bandit sin problemas de seguridad
        bandit_output = {
            "results": [],
            "metrics": {},
        }
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(bandit_output),
            stderr="",
        )

        check = SecurityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Security"
        assert results[0].severity == Severity.INFO
        assert "No security issues" in results[0].message

    @patch("subprocess.run")
    def test_execute_with_high_severity_issue(self, mock_run):
        # Mock de bandit con issue de severidad HIGH
        bandit_output = {
            "results": [
                {
                    "issue_severity": "HIGH",
                    "issue_text": "Use of exec detected",
                    "line_number": 42,
                    "test_id": "B102",
                }
            ],
        }
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=json.dumps(bandit_output),
            stderr="",
        )

        check = SecurityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Security"
        assert results[0].severity == Severity.ERROR  # HIGH → ERROR
        assert "B102" in results[0].message
        assert "exec" in results[0].message
        assert results[0].line_number == 42

    @patch("subprocess.run")
    def test_execute_with_medium_severity_issue(self, mock_run):
        # Mock de bandit con issue de severidad MEDIUM
        bandit_output = {
            "results": [
                {
                    "issue_severity": "MEDIUM",
                    "issue_text": "Possible SQL injection",
                    "line_number": 15,
                    "test_id": "B608",
                }
            ],
        }
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=json.dumps(bandit_output),
            stderr="",
        )

        check = SecurityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].severity == Severity.WARNING  # MEDIUM → WARNING
        assert "SQL injection" in results[0].message
        assert results[0].line_number == 15

    @patch("subprocess.run")
    def test_execute_with_low_severity_issue(self, mock_run):
        # Mock de bandit con issue de severidad LOW
        bandit_output = {
            "results": [
                {
                    "issue_severity": "LOW",
                    "issue_text": "Standard pseudo-random generators are not suitable for security",
                    "line_number": 8,
                    "test_id": "B311",
                }
            ],
        }
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=json.dumps(bandit_output),
            stderr="",
        )

        check = SecurityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].severity == Severity.INFO  # LOW → INFO
        assert "pseudo-random" in results[0].message

    @patch("subprocess.run")
    def test_execute_with_multiple_issues(self, mock_run):
        # Mock de bandit con múltiples issues de diferentes severidades
        bandit_output = {
            "results": [
                {
                    "issue_severity": "HIGH",
                    "issue_text": "Hardcoded password string",
                    "line_number": 10,
                    "test_id": "B105",
                },
                {
                    "issue_severity": "MEDIUM",
                    "issue_text": "Use of insecure MD5 hash",
                    "line_number": 25,
                    "test_id": "B303",
                },
                {
                    "issue_severity": "LOW",
                    "issue_text": "Consider possible security implications",
                    "line_number": 30,
                    "test_id": "B101",
                },
            ],
        }
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=json.dumps(bandit_output),
            stderr="",
        )

        check = SecurityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 3
        # Verificar que cada issue se procesó correctamente
        assert results[0].severity == Severity.ERROR
        assert results[1].severity == Severity.WARNING
        assert results[2].severity == Severity.INFO

    @patch("subprocess.run")
    def test_execute_with_bandit_not_installed(self, mock_run):
        # Mock de FileNotFoundError (bandit no instalado)
        mock_run.side_effect = FileNotFoundError()

        check = SecurityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Security"
        assert results[0].severity == Severity.ERROR
        assert "not installed" in results[0].message

    @patch("subprocess.run")
    def test_execute_with_timeout(self, mock_run):
        # Mock de TimeoutExpired
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="bandit", timeout=10)

        check = SecurityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Security"
        assert results[0].severity == Severity.ERROR
        assert "timed out" in results[0].message

    @patch("subprocess.run")
    def test_execute_with_invalid_json(self, mock_run):
        # Mock de bandit con JSON inválido
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Invalid JSON {{{",
            stderr="",
        )

        check = SecurityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].severity == Severity.ERROR
        assert "parse" in results[0].message.lower()

    @patch("subprocess.run")
    def test_execute_with_unexpected_error(self, mock_run):
        # Mock de error inesperado
        mock_run.side_effect = RuntimeError("Unexpected error")

        check = SecurityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Security"
        assert results[0].severity == Severity.ERROR
        assert "Unexpected error" in results[0].message

    @patch("subprocess.run")
    def test_execute_calls_bandit_with_correct_args(self, mock_run):
        # Verificar que se llama bandit con los argumentos correctos
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"results": []}),
            stderr="",
        )

        check = SecurityCheck()
        check.execute(Path("/tmp/test.py"))

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "bandit"
        assert "-f" in args
        assert "json" in args
        assert "/tmp/test.py" in args


class TestSecurityCheckMapSeverity:
    """Tests para el método _map_severity()."""

    def test_map_high_to_error(self):
        check = SecurityCheck()
        assert check._map_severity("HIGH") == Severity.ERROR

    def test_map_medium_to_warning(self):
        check = SecurityCheck()
        assert check._map_severity("MEDIUM") == Severity.WARNING

    def test_map_low_to_info(self):
        check = SecurityCheck()
        assert check._map_severity("LOW") == Severity.INFO

    def test_map_case_insensitive(self):
        check = SecurityCheck()
        assert check._map_severity("high") == Severity.ERROR
        assert check._map_severity("MeDiUm") == Severity.WARNING
        assert check._map_severity("low") == Severity.INFO

    def test_map_unknown_severity_to_info(self):
        check = SecurityCheck()
        assert check._map_severity("UNKNOWN") == Severity.INFO
        assert check._map_severity("") == Severity.INFO
