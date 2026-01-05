"""
Tests unitarios para CodeGuard.
"""

import pytest
from pathlib import Path

from quality_agents.codeguard import CodeGuard
from quality_agents.codeguard.agent import Severity, CheckResult


class TestCodeGuard:
    """Tests para el agente CodeGuard."""

    def test_init_without_config(self):
        """Debe inicializarse sin configuración."""
        guard = CodeGuard()
        assert guard.config_path is None
        assert guard.results == []

    def test_init_with_config(self, tmp_path):
        """Debe inicializarse con configuración."""
        config_path = tmp_path / "config.yml"
        config_path.touch()

        guard = CodeGuard(config_path=config_path)
        assert guard.config_path == config_path

    def test_run_returns_list(self, sample_python_file):
        """run() debe retornar lista de resultados."""
        guard = CodeGuard()
        results = guard.run([sample_python_file])

        assert isinstance(results, list)

    def test_run_filters_non_python_files(self, temp_project):
        """run() debe ignorar archivos no-Python."""
        txt_file = temp_project / "readme.txt"
        txt_file.write_text("Not Python")

        guard = CodeGuard()
        results = guard.run([txt_file])

        assert results == []


class TestCheckResult:
    """Tests para CheckResult."""

    def test_create_check_result(self):
        """Debe crear CheckResult correctamente."""
        result = CheckResult(
            check_name="test_check",
            severity=Severity.WARNING,
            message="Test message",
            file_path="test.py",
            line_number=10
        )

        assert result.check_name == "test_check"
        assert result.severity == Severity.WARNING
        assert result.message == "Test message"
        assert result.file_path == "test.py"
        assert result.line_number == 10

    def test_check_result_optional_fields(self):
        """Campos opcionales deben ser None por defecto."""
        result = CheckResult(
            check_name="test",
            severity=Severity.INFO,
            message="msg"
        )

        assert result.file_path is None
        assert result.line_number is None


class TestSeverity:
    """Tests para Severity enum."""

    def test_severity_values(self):
        """Debe tener los valores correctos."""
        assert Severity.INFO.value == "info"
        assert Severity.WARNING.value == "warning"
        assert Severity.ERROR.value == "error"
