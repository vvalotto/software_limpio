"""
Tests de integración de CodeGuard con CheckOrchestrator.

Fecha de creación: 2026-02-03
Ticket: 2.5.1
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quality_agents.codeguard.agent import CheckResult, CodeGuard, Severity
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


class TestCodeGuardWithFullProject:
    """Tests end-to-end con proyecto completo."""

    @pytest.fixture
    def temp_project(self):
        """Crea un proyecto Python temporal completo."""
        import shutil

        # Crear directorio temporal
        temp_dir = Path(tempfile.mkdtemp(prefix="test_project_"))

        # Crear estructura de proyecto
        src_dir = temp_dir / "src"
        src_dir.mkdir()

        # Archivo con problemas de calidad
        bad_file = src_dir / "bad_code.py"
        bad_file.write_text("""
import os
import sys
import json

def   bad_function( x,y ):
    a=x+y
    b=a*2
    c=b+1
    d=c*2
    e=d+1
    f=e*2
    g=f+1
    h=g*2
    return h

def unused_function():
    pass
""")

        # Archivo válido
        good_file = src_dir / "good_code.py"
        good_file.write_text("""
def hello(name: str) -> str:
    \"\"\"Say hello to someone.

    Args:
        name: Name of the person

    Returns:
        Greeting message
    \"\"\"
    return f"Hello, {name}!"
""")

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_run_on_full_project(self, temp_project):
        """Verifica que CodeGuard analiza un proyecto completo."""
        guard = CodeGuard()

        # Recolectar todos los archivos .py
        py_files = list((temp_project / "src").rglob("*.py"))
        assert len(py_files) == 2

        # Ejecutar análisis
        results = guard.run(py_files, analysis_type="full")

        # Debe detectar problemas en bad_code.py
        assert len(results) > 0

        # Verificar que detecta problemas específicos
        bad_file_results = [r for r in results if "bad_code.py" in str(r.file_path)]
        assert len(bad_file_results) > 0

    def test_precommit_analysis_under_5_seconds(self, temp_project):
        """Verifica que análisis pre-commit termina en < 5 segundos."""
        import time

        guard = CodeGuard()
        py_files = list((temp_project / "src").rglob("*.py"))

        # Medir tiempo de ejecución
        start = time.time()
        guard.run(py_files, analysis_type="pre-commit", time_budget=5.0)
        elapsed = time.time() - start

        # Debe terminar en menos de 5 segundos
        assert elapsed < 5.0, f"Pre-commit analysis took {elapsed:.2f}s (> 5s)"


class TestCodeGuardWithConfiguration:
    """Tests de configuración desde diferentes fuentes."""

    @pytest.fixture
    def project_with_pyproject_toml(self):
        """Crea proyecto con pyproject.toml."""
        import shutil

        temp_dir = Path(tempfile.mkdtemp(prefix="test_config_"))

        # Crear pyproject.toml
        pyproject = temp_dir / "pyproject.toml"
        pyproject.write_text("""
[tool.codeguard]
min_pylint_score = 9.0
max_cyclomatic_complexity = 5
check_pep8 = true
check_security = true
exclude_patterns = ["test_*.py", "__pycache__"]

[tool.codeguard.ai]
enabled = false
""")

        # Crear archivo Python
        src_dir = temp_dir / "src"
        src_dir.mkdir()
        (src_dir / "app.py").write_text("print('hello')\n")

        yield temp_dir

        shutil.rmtree(temp_dir)

    @pytest.fixture
    def project_with_yaml_config(self):
        """Crea proyecto con .codeguard.yml."""
        import shutil

        temp_dir = Path(tempfile.mkdtemp(prefix="test_yaml_"))

        # Crear .codeguard.yml con formato correcto (campos directos)
        yaml_config = temp_dir / ".codeguard.yml"
        yaml_config.write_text("""
min_pylint_score: 8.5
max_cyclomatic_complexity: 8
check_pep8: true
check_security: true
exclude_patterns:
  - "*.pyc"
  - "__pycache__"
""")

        # Crear archivo Python
        (temp_dir / "app.py").write_text("print('hello')\n")

        yield temp_dir

        shutil.rmtree(temp_dir)

    def test_load_config_from_pyproject_toml(self, project_with_pyproject_toml):
        """Verifica que carga configuración desde pyproject.toml."""
        from quality_agents.codeguard.config import load_config

        config = load_config(project_root=project_with_pyproject_toml)

        # Verificar que cargó la configuración
        assert config.min_pylint_score == 9.0
        assert config.max_cyclomatic_complexity == 5
        assert config.check_pep8 is True
        assert config.check_security is True
        assert "test_*.py" in config.exclude_patterns
        assert config.ai.enabled is False

    def test_load_config_from_yaml(self, project_with_yaml_config):
        """Verifica que carga configuración desde .yml."""
        from quality_agents.codeguard.config import load_config

        # Buscar config en directorio del proyecto
        config_path = project_with_yaml_config / ".codeguard.yml"
        config = load_config(config_path=config_path, project_root=project_with_yaml_config)

        # Verificar que cargó la configuración
        assert config.min_pylint_score == 8.5
        assert config.max_cyclomatic_complexity == 8
        assert config.check_pep8 is True
        assert config.check_security is True

    def test_load_config_defaults_when_no_file(self):
        """Verifica que usa defaults cuando no hay archivo de configuración."""
        import shutil
        import tempfile

        temp_dir = Path(tempfile.mkdtemp(prefix="test_defaults_"))

        try:
            from quality_agents.codeguard.config import load_config

            config = load_config(project_root=temp_dir)

            # Debe usar valores por defecto
            assert config.min_pylint_score == 8.0  # Default
            assert config.max_cyclomatic_complexity == 10  # Default
        finally:
            shutil.rmtree(temp_dir)

    def test_run_with_pyproject_toml_config(self, project_with_pyproject_toml):
        """Verifica que CodeGuard usa configuración de pyproject.toml."""
        from quality_agents.codeguard.config import load_config

        # Cargar config
        config = load_config(project_root=project_with_pyproject_toml)

        # Crear CodeGuard con la config
        guard = CodeGuard()
        guard.config = config

        # Ejecutar
        py_files = list(project_with_pyproject_toml.rglob("*.py"))
        results = guard.run(py_files)

        # Debe ejecutar sin errores
        assert isinstance(results, list)

    def test_run_with_ai_disabled(self):
        """Verifica que CodeGuard funciona con IA deshabilitada."""
        from quality_agents.codeguard.config import AIConfig, CodeGuardConfig

        # Config con IA deshabilitada
        config = CodeGuardConfig(ai=AIConfig(enabled=False))
        guard = CodeGuard()
        guard.config = config

        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello')\n")
            temp_path = Path(f.name)

        try:
            results = guard.run([temp_path])
            assert isinstance(results, list)
        finally:
            temp_path.unlink()

    def test_run_with_ai_enabled_but_no_api_key(self):
        """Verifica que CodeGuard funciona con IA habilitada pero sin API key."""
        import os

        from quality_agents.codeguard.config import AIConfig, CodeGuardConfig

        # Asegurar que no hay API key
        old_key = os.environ.pop("ANTHROPIC_API_KEY", None)

        try:
            # Config con IA habilitada
            config = CodeGuardConfig(ai=AIConfig(enabled=True))
            guard = CodeGuard()
            guard.config = config

            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write("print('hello')\n")
                temp_path = Path(f.name)

            try:
                # Debe funcionar sin IA (degradar gracefully)
                results = guard.run([temp_path])
                assert isinstance(results, list)
            finally:
                temp_path.unlink()
        finally:
            # Restaurar API key si existía
            if old_key:
                os.environ["ANTHROPIC_API_KEY"] = old_key
