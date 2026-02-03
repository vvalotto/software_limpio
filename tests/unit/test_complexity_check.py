"""
Tests unitarios para ComplexityCheck.

Fecha de creación: 2026-02-03
Ticket: 2.4
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quality_agents.codeguard.agent import CheckResult, Severity
from quality_agents.codeguard.checks.complexity_check import ComplexityCheck
from quality_agents.codeguard.config import CodeGuardConfig
from quality_agents.shared.verifiable import ExecutionContext


class TestComplexityCheckProperties:
    """Tests para las propiedades de ComplexityCheck."""

    def test_name(self):
        check = ComplexityCheck()
        assert check.name == "Complexity"

    def test_category(self):
        check = ComplexityCheck()
        assert check.category == "complexity"

    def test_estimated_duration(self):
        check = ComplexityCheck()
        assert check.estimated_duration == 1.0

    def test_priority(self):
        check = ComplexityCheck()
        assert check.priority == 3


class TestComplexityCheckShouldRun:
    """Tests para el método should_run()."""

    def test_should_run_on_python_file(self):
        check = ComplexityCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(check_complexity=True),
        )
        assert check.should_run(context) is True

    def test_should_not_run_on_excluded_file(self):
        check = ComplexityCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=True,
            config=CodeGuardConfig(check_complexity=True),
        )
        assert check.should_run(context) is False

    def test_should_not_run_on_non_python_file(self):
        check = ComplexityCheck()
        context = ExecutionContext(
            file_path=Path("test.txt"),
            is_excluded=False,
            config=CodeGuardConfig(check_complexity=True),
        )
        assert check.should_run(context) is False

    def test_should_not_run_when_disabled_in_config(self):
        check = ComplexityCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(check_complexity=False),
        )
        assert check.should_run(context) is False

    def test_should_run_when_config_is_none(self):
        # Si no hay config, asumir que está habilitado
        check = ComplexityCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=None,
        )
        assert check.should_run(context) is True


class TestComplexityCheckExecute:
    """Tests para el método execute()."""

    @patch("subprocess.run")
    def test_execute_with_no_complex_functions(self, mock_run):
        # Mock de radon sin funciones complejas
        radon_output = """test.py
    F 1:0 simple_function - A (2)
    F 5:0 another_simple - A (3)
"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=radon_output,
            stderr="",
        )

        check = ComplexityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Complexity"
        assert results[0].severity == Severity.INFO
        assert "below complexity threshold" in results[0].message or "No complex" in results[0].message
        assert results[0].file_path == "test.py"

    @patch("subprocess.run")
    def test_execute_with_complex_function_warning(self, mock_run):
        # Mock de radon con función moderadamente compleja (CC=12)
        radon_output = """test.py
    F 10:0 complex_function - C (12)
"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=radon_output,
            stderr="",
        )

        check = ComplexityCheck()
        # Inyectar contexto con config
        check._context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(max_cyclomatic_complexity=10),
        )
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Complexity"
        assert results[0].severity == Severity.WARNING
        assert "complex_function" in results[0].message
        assert "12" in results[0].message
        assert "grade C" in results[0].message
        assert results[0].line_number == 10

    @patch("subprocess.run")
    def test_execute_with_very_complex_function_error(self, mock_run):
        # Mock de radon con función muy compleja (CC=25)
        radon_output = """test.py
    F 15:0 very_complex_function - D (25)
"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=radon_output,
            stderr="",
        )

        check = ComplexityCheck()
        check._context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(max_cyclomatic_complexity=10),
        )
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Complexity"
        assert results[0].severity == Severity.ERROR
        assert "very_complex_function" in results[0].message
        assert "25" in results[0].message
        assert "grade D" in results[0].message
        assert results[0].line_number == 15

    @patch("subprocess.run")
    def test_execute_with_multiple_complex_functions(self, mock_run):
        # Mock de radon con múltiples funciones complejas
        radon_output = """test.py
    F 10:0 function1 - C (12)
    M 20:4 Class.method1 - C (15)
    F 30:0 function2 - B (8)
"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=radon_output,
            stderr="",
        )

        check = ComplexityCheck()
        check._context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(max_cyclomatic_complexity=10),
        )
        results = check.execute(Path("test.py"))

        # Debería reportar las 2 funciones que exceden el umbral (12 y 15)
        # La de CC=8 no se reporta porque está por debajo
        assert len(results) == 2
        assert all(r.check_name == "Complexity" for r in results)

        # Verificar que se reportaron las funciones correctas
        messages = [r.message for r in results]
        assert any("function1" in msg and "12" in msg for msg in messages)
        assert any("Class.method1" in msg and "15" in msg for msg in messages)

    @patch("subprocess.run")
    def test_execute_with_empty_output(self, mock_run):
        # Mock de radon con archivo vacío o sin funciones
        radon_output = """test.py
"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=radon_output,
            stderr="",
        )

        check = ComplexityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].severity == Severity.INFO
        assert "No complex" in results[0].message

    @patch("subprocess.run")
    def test_execute_radon_not_installed(self, mock_run):
        # Mock de FileNotFoundError (radon no instalado)
        mock_run.side_effect = FileNotFoundError()

        check = ComplexityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Complexity"
        assert results[0].severity == Severity.ERROR
        assert "not installed" in results[0].message
        assert "pip install radon" in results[0].message

    @patch("subprocess.run")
    def test_execute_timeout(self, mock_run):
        # Mock de timeout
        mock_run.side_effect = subprocess.TimeoutExpired("radon", 5)

        check = ComplexityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Complexity"
        assert results[0].severity == Severity.ERROR
        assert "timed out" in results[0].message

    @patch("subprocess.run")
    def test_execute_unexpected_error(self, mock_run):
        # Mock de error inesperado
        mock_run.side_effect = RuntimeError("Unexpected error")

        check = ComplexityCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Complexity"
        assert results[0].severity == Severity.ERROR
        assert "Unexpected error" in results[0].message


class TestComplexityCheckParseRadonOutput:
    """Tests para el método _parse_radon_output()."""

    def test_parse_simple_output(self):
        check = ComplexityCheck()
        output = """test.py
    F 10:0 simple_function - A (2)
"""
        functions = check._parse_radon_output(output)

        assert len(functions) == 1
        assert functions[0]["line"] == 10
        assert functions[0]["name"] == "simple_function"
        assert functions[0]["grade"] == "A"
        assert functions[0]["complexity"] == 2

    def test_parse_multiple_functions(self):
        check = ComplexityCheck()
        output = """test.py
    F 10:0 function1 - B (8)
    M 20:4 Class.method1 - C (12)
    F 30:0 function2 - A (3)
"""
        functions = check._parse_radon_output(output)

        assert len(functions) == 3
        assert functions[0]["name"] == "function1"
        assert functions[0]["complexity"] == 8
        assert functions[1]["name"] == "Class.method1"
        assert functions[1]["complexity"] == 12
        assert functions[2]["name"] == "function2"
        assert functions[2]["complexity"] == 3

    def test_parse_empty_output(self):
        check = ComplexityCheck()
        output = ""
        functions = check._parse_radon_output(output)

        assert len(functions) == 0

    def test_parse_output_with_different_grades(self):
        check = ComplexityCheck()
        output = """test.py
    F 10:0 grade_a - A (5)
    F 20:0 grade_b - B (10)
    F 30:0 grade_c - C (15)
    F 40:0 grade_d - D (25)
    F 50:0 grade_e - E (60)
    F 60:0 grade_f - F (120)
"""
        functions = check._parse_radon_output(output)

        assert len(functions) == 6
        grades = [f["grade"] for f in functions]
        assert grades == ["A", "B", "C", "D", "E", "F"]
        complexities = [f["complexity"] for f in functions]
        assert complexities == [5, 10, 15, 25, 60, 120]


class TestComplexityCheckMapSeverity:
    """Tests para el método _map_severity()."""

    def test_map_severity_below_threshold(self):
        check = ComplexityCheck()
        severity = check._map_severity(complexity=8, max_cc=10)
        assert severity == Severity.INFO

    def test_map_severity_at_threshold(self):
        check = ComplexityCheck()
        severity = check._map_severity(complexity=10, max_cc=10)
        assert severity == Severity.INFO

    def test_map_severity_slightly_above_threshold(self):
        check = ComplexityCheck()
        severity = check._map_severity(complexity=12, max_cc=10)
        assert severity == Severity.WARNING

    def test_map_severity_moderately_complex(self):
        check = ComplexityCheck()
        severity = check._map_severity(complexity=20, max_cc=10)
        assert severity == Severity.WARNING

    def test_map_severity_very_complex(self):
        check = ComplexityCheck()
        severity = check._map_severity(complexity=21, max_cc=10)
        assert severity == Severity.ERROR

    def test_map_severity_extremely_complex(self):
        check = ComplexityCheck()
        severity = check._map_severity(complexity=100, max_cc=10)
        assert severity == Severity.ERROR
