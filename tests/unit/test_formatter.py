"""
Tests para formatter.py (Rich output)

Fecha de creación: 2026-02-04
Ticket: 4.1 - Implementar formatter con Rich
"""

from io import StringIO
from unittest.mock import patch

import pytest
from rich.console import Console

from quality_agents.codeguard.agent import CheckResult, Severity
from quality_agents.codeguard.formatter import (
    format_results,
    _print_header,
    _print_stats,
    _print_success,
    _print_results_table,
    _print_summary,
    _print_suggestions,
)


class TestFormatResults:
    """Tests para la función principal format_results()."""

    def test_format_results_no_problems(self, capsys):
        """Test con cero problemas (éxito)."""
        results = []
        format_results(results, elapsed=2.5, total_files=10, checks_executed=6)

        captured = capsys.readouterr()
        assert "CodeGuard" in captured.out
        assert "No se encontraron problemas" in captured.out
        assert "2.50s" in captured.out

    def test_format_results_with_errors(self, capsys):
        """Test con errores."""
        results = [
            CheckResult(
                check_name="PEP8",
                severity=Severity.ERROR,
                message="Line too long (120 > 100)",
                file_path="src/app.py",
                line_number=42,
            ),
        ]

        format_results(results, elapsed=1.2, total_files=5, checks_executed=3)

        captured = capsys.readouterr()
        assert "Errores" in captured.out
        assert "PEP8" in captured.out
        assert "src/app.py:42" in captured.out
        assert "Line too long" in captured.out

    def test_format_results_with_warnings(self, capsys):
        """Test con advertencias."""
        results = [
            CheckResult(
                check_name="Pylint",
                severity=Severity.WARNING,
                message="Pylint score: 7.5/10 (threshold: 8.0)",
                file_path="src/utils.py",
            ),
        ]

        format_results(results, elapsed=3.1, total_files=8, checks_executed=4)

        captured = capsys.readouterr()
        assert "Advertencias" in captured.out
        assert "Pylint" in captured.out
        assert "7.5/10" in captured.out

    def test_format_results_with_infos(self, capsys):
        """Test con informativos."""
        results = [
            CheckResult(
                check_name="Complexity",
                severity=Severity.INFO,
                message="Function 'process_data' has complexity 12",
                file_path="src/processor.py",
                line_number=100,
            ),
        ]

        format_results(results, elapsed=2.0, total_files=3, checks_executed=2)

        captured = capsys.readouterr()
        assert "Informativos" in captured.out
        assert "Complexity" in captured.out
        assert "process_data" in captured.out

    def test_format_results_mixed_severity(self, capsys):
        """Test con múltiples severidades."""
        results = [
            CheckResult(
                check_name="Security",
                severity=Severity.ERROR,
                message="Hardcoded password detected",
                file_path="src/config.py",
                line_number=10,
            ),
            CheckResult(
                check_name="PEP8",
                severity=Severity.WARNING,
                message="Missing docstring",
                file_path="src/helpers.py",
                line_number=5,
            ),
            CheckResult(
                check_name="Complexity",
                severity=Severity.INFO,
                message="Complexity: 8",
                file_path="src/main.py",
            ),
        ]

        format_results(results, elapsed=4.5, total_files=15, checks_executed=6)

        captured = capsys.readouterr()
        assert "Errores (1)" in captured.out
        assert "Advertencias (1)" in captured.out
        assert "Informativos (1)" in captured.out
        assert "Security" in captured.out
        assert "PEP8" in captured.out
        assert "Complexity" in captured.out


class TestPrintHeader:
    """Tests para _print_header()."""

    def test_print_header(self, capsys):
        """Test que imprime header correctamente."""
        console = Console()
        _print_header(console)

        captured = capsys.readouterr()
        assert "CodeGuard" in captured.out
        assert "Control de Calidad" in captured.out


class TestPrintStats:
    """Tests para _print_stats()."""

    def test_print_stats(self, capsys):
        """Test que imprime estadísticas."""
        console = Console()
        results = [
            CheckResult("Test", Severity.ERROR, "test"),
            CheckResult("Test", Severity.WARNING, "test"),
        ]

        _print_stats(console, results, elapsed=3.14, total_files=10, checks_executed=5)

        captured = capsys.readouterr()
        assert "10" in captured.out  # archivos
        assert "5" in captured.out  # checks
        assert "3.14s" in captured.out  # tiempo
        assert "2" in captured.out  # resultados


class TestPrintSuccess:
    """Tests para _print_success()."""

    def test_print_success(self, capsys):
        """Test mensaje de éxito."""
        console = Console()
        _print_success(console)

        captured = capsys.readouterr()
        assert "No se encontraron problemas" in captured.out


class TestPrintResultsTable:
    """Tests para _print_results_table()."""

    def test_print_results_table_with_line_numbers(self, capsys):
        """Test tabla con números de línea."""
        console = Console()
        results = [
            CheckResult(
                check_name="PEP8",
                severity=Severity.ERROR,
                message="Line too long",
                file_path="src/app.py",
                line_number=42,
            ),
        ]

        _print_results_table(console, results, "Errores", "red")

        captured = capsys.readouterr()
        assert "Errores (1)" in captured.out
        assert "PEP8" in captured.out
        assert "src/app.py:42" in captured.out
        assert "Line too long" in captured.out

    def test_print_results_table_without_line_numbers(self, capsys):
        """Test tabla sin números de línea."""
        console = Console()
        results = [
            CheckResult(
                check_name="Pylint",
                severity=Severity.WARNING,
                message="Low score",
                file_path="src/utils.py",
            ),
        ]

        _print_results_table(console, results, "Advertencias", "yellow")

        captured = capsys.readouterr()
        assert "Advertencias (1)" in captured.out
        assert "Pylint" in captured.out
        assert "src/utils.py" in captured.out

    def test_print_results_table_truncates_long_messages(self, capsys):
        """Test que trunca mensajes muy largos."""
        console = Console()
        long_message = "A" * 150  # Mensaje de 150 caracteres
        results = [
            CheckResult(
                check_name="Test",
                severity=Severity.INFO,
                message=long_message,
                file_path="test.py",
            ),
        ]

        _print_results_table(console, results, "Test", "blue")

        captured = capsys.readouterr()
        # Debe truncar y agregar ... o … (unicode ellipsis)
        assert ("..." in captured.out or "…" in captured.out)
        # Rich trunca automáticamente por max_width, verificar que se muestra
        assert "Test" in captured.out


class TestPrintSummary:
    """Tests para _print_summary()."""

    def test_print_summary_with_all_severities(self, capsys):
        """Test resumen con todas las severidades."""
        console = Console()
        errors = [CheckResult("E1", Severity.ERROR, "error")]
        warnings = [CheckResult("W1", Severity.WARNING, "warn")]
        infos = [CheckResult("I1", Severity.INFO, "info")]

        _print_summary(console, errors, warnings, infos)

        captured = capsys.readouterr()
        assert "Resumen" in captured.out
        assert "1 errores" in captured.out or "1 error" in captured.out
        assert "1 advertencias" in captured.out or "1 advertencia" in captured.out
        assert "1 informativos" in captured.out

    def test_print_summary_no_problems(self, capsys):
        """Test resumen sin problemas."""
        console = Console()
        _print_summary(console, [], [], [])

        captured = capsys.readouterr()
        assert "Resumen" in captured.out
        assert "0 errores" in captured.out or "0 error" in captured.out


class TestPrintSuggestions:
    """Tests para _print_suggestions()."""

    def test_suggestions_for_pep8(self, capsys):
        """Test sugerencia para PEP8."""
        console = Console()
        errors = [CheckResult("PEP8", Severity.ERROR, "error", "test.py")]

        _print_suggestions(console, errors, [])

        captured = capsys.readouterr()
        assert "Sugerencias" in captured.out
        assert "black" in captured.out

    def test_suggestions_for_unused_imports(self, capsys):
        """Test sugerencia para imports."""
        console = Console()
        warnings = [CheckResult("UnusedImports", Severity.WARNING, "warn", "test.py")]

        _print_suggestions(console, [], warnings)

        captured = capsys.readouterr()
        assert "autoflake" in captured.out

    def test_suggestions_for_complexity(self, capsys):
        """Test sugerencia para complejidad."""
        console = Console()
        infos = [CheckResult("Complexity", Severity.INFO, "info", "test.py")]

        _print_suggestions(console, [], infos)

        captured = capsys.readouterr()
        assert "Refactoriza" in captured.out or "funciones más pequeñas" in captured.out

    def test_suggestions_for_security(self, capsys):
        """Test sugerencia para seguridad."""
        console = Console()
        errors = [CheckResult("Security", Severity.ERROR, "vuln", "test.py")]

        _print_suggestions(console, errors, [])

        captured = capsys.readouterr()
        assert "Seguridad" in captured.out or "CRÍTICO" in captured.out

    def test_no_suggestions_when_no_problems(self, capsys):
        """Test sin sugerencias cuando no hay problemas."""
        console = Console()
        _print_suggestions(console, [], [])

        captured = capsys.readouterr()
        # No debe imprimir nada
        assert "Sugerencias" not in captured.out
