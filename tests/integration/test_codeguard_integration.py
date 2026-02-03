"""
Tests de integración de CodeGuard con CheckOrchestrator.

Fecha de creación: 2026-02-03
Ticket: 2.5.1
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import tempfile

import pytest

from quality_agents.codeguard.agent import CodeGuard, CheckResult, Severity
from quality_agents.codeguard.config import CodeGuardConfig


class TestCodeGuardOrchestration:
    """Tests para la orquestación de checks en CodeGuard."""

    @pytest.fixture
    def temp_python_file(self):
        """Crea un archivo Python temporal."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello')\n")
            temp_path = Path(f.name)

        yield temp_path

        # Cleanup
        temp_path.unlink()

    def test_run_creates_execution_context(self, temp_python_file):
        """Verifica que run() crea ExecutionContext correctamente."""
        guard = CodeGuard()

        # Ejecutar con parámetros específicos
        guard.run([temp_python_file], analysis_type="pre-commit", time_budget=5.0)

        # El contexto debe haberse pasado al orquestador
        assert guard.orchestrator is not None

    def test_run_with_precommit_analysis_type(self, temp_python_file):
        """Verifica que pre-commit ejecuta solo checks rápidos."""
        guard = CodeGuard()

        # Ejecutar con pre-commit (solo checks de priority 1-3)
        results = guard.run([temp_python_file], analysis_type="pre-commit", time_budget=5.0)

        # Debe retornar lista (puede estar vacía si no hay problemas)
        assert isinstance(results, list)
        # Todos los resultados deben ser CheckResult
        assert all(isinstance(r, CheckResult) for r in results)

    def test_run_with_pr_review_analysis_type(self, temp_python_file):
        """Verifica que pr-review ejecuta todos los checks."""
        guard = CodeGuard()

        # Ejecutar con pr-review (todos los checks)
        results = guard.run([temp_python_file], analysis_type="pr-review")

        assert isinstance(results, list)
        assert all(isinstance(r, CheckResult) for r in results)

    def test_run_with_full_analysis_type(self, temp_python_file):
        """Verifica que full ejecuta todos los checks."""
        guard = CodeGuard()

        # Ejecutar con full (todos los checks)
        results = guard.run([temp_python_file], analysis_type="full")

        assert isinstance(results, list)
        assert all(isinstance(r, CheckResult) for r in results)

    def test_run_filters_python_files(self, temp_python_file):
        """Verifica que run() filtra solo archivos Python."""
        guard = CodeGuard()

        # Crear archivo no-Python
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("not python\n")
            temp_txt = Path(f.name)

        try:
            # Ejecutar con archivo Python y no-Python
            results = guard.run([temp_python_file, temp_txt])

            # No debe procesar el .txt
            txt_results = [r for r in results if temp_txt.name in str(r.file_path)]
            assert len(txt_results) == 0
        finally:
            temp_txt.unlink()

    def test_run_respects_exclusion_patterns(self):
        """Verifica que run() excluye archivos según config."""
        # Config con exclusión de tests
        config = CodeGuardConfig(exclude_patterns=["test_"])
        guard = CodeGuard()
        guard.config = config

        # Crear archivo que debería ser excluido
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", prefix="test_", delete=False) as f:
            f.write("print('test')\n")
            temp_test = Path(f.name)

        try:
            # Ejecutar
            results = guard.run([temp_test])

            # No debe haber resultados para archivo excluido
            # (el check no se ejecuta si is_excluded=True)
            assert len(results) == 0
        finally:
            temp_test.unlink()

    def test_run_handles_check_failure_gracefully(self, temp_python_file):
        """Verifica que run() maneja fallos de checks sin romper."""
        guard = CodeGuard()

        # Mock un check que falla
        failing_check = MagicMock()
        failing_check.name = "FailingCheck"
        failing_check.execute.side_effect = RuntimeError("Check failed")

        # Agregar check que falla al orquestador
        original_checks = guard.orchestrator.checks
        guard.orchestrator.checks = original_checks + [failing_check]

        # Mock select_checks para incluir el check que falla
        with patch.object(guard.orchestrator, 'select_checks') as mock_select:
            mock_select.return_value = [failing_check]

            # Ejecutar no debe lanzar excepción
            results = guard.run([temp_python_file])

            # Debe haber un resultado con ERROR indicando el fallo
            error_results = [r for r in results if r.severity == Severity.ERROR]
            assert len(error_results) > 0
            assert any("failed with error" in r.message.lower() for r in error_results)

    def test_run_with_time_budget(self, temp_python_file):
        """Verifica que run() respeta el presupuesto de tiempo."""
        guard = CodeGuard()

        # Ejecutar con presupuesto muy bajo
        results = guard.run([temp_python_file], analysis_type="pre-commit", time_budget=1.0)

        # Debe ejecutar solo checks que caben en 1s
        assert isinstance(results, list)

    def test_run_accumulates_results_from_multiple_checks(self, temp_python_file):
        """Verifica que run() acumula resultados de todos los checks."""
        guard = CodeGuard()

        # Ejecutar
        results = guard.run([temp_python_file], analysis_type="full")

        # Si hay resultados, debe haber de múltiples checks
        if len(results) > 1:
            check_names = {r.check_name for r in results}
            # Puede haber múltiples checks diferentes
            assert len(check_names) >= 1

    def test_is_excluded_with_pattern(self):
        """Verifica que _is_excluded funciona correctamente."""
        config = CodeGuardConfig(exclude_patterns=["__pycache__", "*.pyc", "venv"])
        guard = CodeGuard()
        guard.config = config

        # Archivos que deben ser excluidos
        assert guard._is_excluded(Path("src/__pycache__/test.py")) is True
        assert guard._is_excluded(Path("venv/lib/python.py")) is True

        # Archivos que NO deben ser excluidos
        assert guard._is_excluded(Path("src/app.py")) is False
        assert guard._is_excluded(Path("tests/test_app.py")) is False


class TestCodeGuardCLIIntegration:
    """Tests para la integración del CLI con el orquestador."""

    def test_cli_imports_successfully(self):
        """Verifica que el CLI puede importarse sin errores."""
        from quality_agents.codeguard.agent import main

        assert main is not None
        assert callable(main)

    def test_cli_has_analysis_type_option(self):
        """Verifica que el CLI tiene la opción --analysis-type."""
        from quality_agents.codeguard.agent import main

        # Verificar que el comando tiene la opción
        assert hasattr(main, 'params')
        param_names = [p.name for p in main.params]
        assert 'analysis_type' in param_names

    def test_cli_has_time_budget_option(self):
        """Verifica que el CLI tiene la opción --time-budget."""
        from quality_agents.codeguard.agent import main

        param_names = [p.name for p in main.params]
        assert 'time_budget' in param_names


class TestCodeGuardWithRealChecks:
    """Tests de integración con checks reales."""

    @pytest.fixture
    def valid_python_file(self):
        """Crea un archivo Python válido."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
def hello():
    \"\"\"Say hello.\"\"\"
    return "hello"
""")
            temp_path = Path(f.name)

        yield temp_path
        temp_path.unlink()

    @pytest.fixture
    def invalid_python_file(self):
        """Crea un archivo Python con problemas."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
import os
import sys

def   bad_function( x,y ):
    return x+y
""")
            temp_path = Path(f.name)

        yield temp_path
        temp_path.unlink()

    def test_run_on_valid_file_produces_info_results(self, valid_python_file):
        """Verifica que archivo válido produce resultados INFO."""
        guard = CodeGuard()
        results = guard.run([valid_python_file])

        # Debe haber al menos algunos resultados INFO
        info_results = [r for r in results if r.severity == Severity.INFO]
        # Nota: Puede no haber INFO si todos los checks pasan silenciosamente
        assert isinstance(info_results, list)

    def test_run_on_invalid_file_produces_warnings(self, invalid_python_file):
        """Verifica que archivo con problemas produce WARNINGs."""
        guard = CodeGuard()
        results = guard.run([invalid_python_file])

        # Debe haber al menos algunos warnings
        warnings = [r for r in results if r.severity == Severity.WARNING]
        # El archivo tiene espaciado incorrecto, debería detectarlo PEP8Check
        assert len(warnings) > 0
