"""
Tests unitarios para DesignReviewer.

Ticket: 1.3 — Refactorizar DesignReviewer como clase principal
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from quality_agents.designreviewer import DesignReviewer
from quality_agents.designreviewer.agent import ReviewResult, ReviewSeverity, main


class TestDesignReviewer:
    """Tests para el agente DesignReviewer."""

    def test_init_default(self):
        """Debe inicializarse con valores por defecto."""
        reviewer = DesignReviewer()

        assert reviewer.path == Path(".")
        assert reviewer.config_path is None
        assert reviewer.results == []

    def test_init_with_path(self, tmp_path):
        """Debe aceptar path y config_path."""
        reviewer = DesignReviewer(path=tmp_path, config_path=None)

        assert reviewer.path == tmp_path

    def test_run_returns_list(self, tmp_path):
        """run() debe retornar lista de resultados."""
        reviewer = DesignReviewer(path=tmp_path)
        results = reviewer.run()

        assert isinstance(results, list)

    def test_run_with_empty_files(self):
        """run() con lista vacía debe retornar lista vacía."""
        reviewer = DesignReviewer()
        results = reviewer.run(files=[])

        assert results == []

    def test_analyze_delta_returns_list(self, tmp_path):
        """analyze_delta() debe retornar lista de resultados."""
        reviewer = DesignReviewer(path=tmp_path)
        results = reviewer.analyze_delta(changed_files=[])

        assert isinstance(results, list)

    def test_should_block_no_criticals(self):
        """should_block() debe retornar False sin resultados CRITICAL."""
        reviewer = DesignReviewer()
        reviewer.results = [
            ReviewResult(
                analyzer_name="TestAnalyzer",
                severity=ReviewSeverity.WARNING,
                current_value=5,
                threshold=10,
                message="Warning de prueba",
                file_path=Path("src/foo.py"),
            )
        ]

        assert reviewer.should_block() is False

    def test_should_block_with_critical(self):
        """should_block() debe retornar True con al menos un resultado CRITICAL."""
        reviewer = DesignReviewer()
        reviewer.results = [
            ReviewResult(
                analyzer_name="TestAnalyzer",
                severity=ReviewSeverity.CRITICAL,
                current_value=15,
                threshold=10,
                message="Violación crítica",
                file_path=Path("src/foo.py"),
            )
        ]

        assert reviewer.should_block() is True

    def test_collect_files_from_file(self, tmp_path):
        """collect_files() con archivo Python debe retornar ese archivo."""
        py_file = tmp_path / "module.py"
        py_file.write_text("x = 1")

        reviewer = DesignReviewer()
        files = reviewer.collect_files(py_file)

        assert files == [py_file]

    def test_collect_files_ignores_non_python(self, tmp_path):
        """collect_files() con archivo no Python debe retornar lista vacía."""
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("hello")

        reviewer = DesignReviewer()
        files = reviewer.collect_files(txt_file)

        assert files == []

    def test_collect_files_from_directory(self, tmp_path):
        """collect_files() con directorio debe encontrar archivos Python recursivamente."""
        (tmp_path / "a.py").write_text("x = 1")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "b.py").write_text("y = 2")

        reviewer = DesignReviewer()
        files = reviewer.collect_files(tmp_path)

        assert len(files) == 2

    def test_collect_files_excluye_venv(self, tmp_path):
        """collect_files() debe excluir archivos dentro de .venv/ (fix #39)."""
        (tmp_path / "modulo.py").write_text("x = 1")
        venv = tmp_path / ".venv" / "lib"
        venv.mkdir(parents=True)
        (venv / "dep.py").write_text("y = 2")
        reviewer = DesignReviewer(path=tmp_path)
        files = reviewer.collect_files(tmp_path)
        assert len(files) == 1
        assert files[0].name == "modulo.py"

    def test_collect_files_excluye_pycache(self, tmp_path):
        """collect_files() debe excluir archivos dentro de __pycache__/."""
        (tmp_path / "modulo.py").write_text("x = 1")
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (cache / "generated.py").write_text("z = 3")
        reviewer = DesignReviewer(path=tmp_path)
        files = reviewer.collect_files(tmp_path)
        assert len(files) == 1
        assert files[0].name == "modulo.py"

    def test_collect_files_excluye_test_files(self, tmp_path):
        """collect_files() debe excluir archivos con 'test_' en su path relativo."""
        (tmp_path / "servicio.py").write_text("x = 1")
        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_servicio.py").write_text("def test_foo(): pass")
        reviewer = DesignReviewer(path=tmp_path)
        files = reviewer.collect_files(tmp_path)
        assert len(files) == 1
        assert files[0].name == "servicio.py"

    def test_collect_files_sin_exclude_patterns(self, tmp_path):
        """Sin exclude_patterns retorna todos los .py."""
        from quality_agents.designreviewer.config import DesignReviewerConfig
        (tmp_path / "a.py").write_text("x = 1")
        venv = tmp_path / ".venv"
        venv.mkdir()
        (venv / "b.py").write_text("y = 2")
        reviewer = DesignReviewer(path=tmp_path)
        reviewer._config = DesignReviewerConfig(exclude_patterns=[])
        files = reviewer.collect_files(tmp_path)
        assert len(files) == 2


class TestReviewResult:
    """Tests para ReviewResult."""

    def test_create_review_result(self):
        """Debe crear ReviewResult correctamente con campos requeridos."""
        result = ReviewResult(
            analyzer_name="CBOAnalyzer",
            severity=ReviewSeverity.WARNING,
            current_value=7,
            threshold=5,
            message="Alto acoplamiento detectado",
            file_path=Path("src/service.py"),
        )

        assert result.analyzer_name == "CBOAnalyzer"
        assert result.current_value == 7
        assert result.threshold == 5
        assert result.file_path == Path("src/service.py")

    def test_create_with_optional_fields(self):
        """Debe aceptar campos opcionales."""
        result = ReviewResult(
            analyzer_name="LCOMAnalyzer",
            severity=ReviewSeverity.WARNING,
            current_value=3,
            threshold=1,
            message="Baja cohesión",
            file_path=Path("src/model.py"),
            class_name="UserModel",
            suggestion="Considerar separar en dos clases",
            estimated_effort=2.5,
        )

        assert result.class_name == "UserModel"
        assert result.suggestion is not None
        assert result.estimated_effort == 2.5

    def test_estimated_effort_default(self):
        """estimated_effort debe ser 0.0 por defecto."""
        result = ReviewResult(
            analyzer_name="CBOAnalyzer",
            severity=ReviewSeverity.INFO,
            current_value=2,
            threshold=5,
            message="OK",
            file_path=Path("src/foo.py"),
        )

        assert result.estimated_effort == 0.0

    def test_is_blocking_critical(self):
        """is_blocking() debe retornar True para CRITICAL."""
        result = ReviewResult(
            analyzer_name="CBOAnalyzer",
            severity=ReviewSeverity.CRITICAL,
            current_value=10,
            threshold=5,
            message="CBO excesivo",
            file_path=Path("src/foo.py"),
        )

        assert result.is_blocking() is True

    def test_is_blocking_warning(self):
        """is_blocking() debe retornar False para WARNING."""
        result = ReviewResult(
            analyzer_name="FanOutAnalyzer",
            severity=ReviewSeverity.WARNING,
            current_value=8,
            threshold=7,
            message="Fan-out elevado",
            file_path=Path("src/foo.py"),
        )

        assert result.is_blocking() is False


class TestReviewSeverity:
    """Tests para ReviewSeverity enum."""

    def test_severity_values(self):
        """Debe tener los valores correctos."""
        assert ReviewSeverity.INFO.value == "info"
        assert ReviewSeverity.WARNING.value == "warning"
        assert ReviewSeverity.CRITICAL.value == "critical"


class TestDesignReviewerCLI:
    """Tests del CLI de DesignReviewer (fix #41)."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_path_unico_aceptado(self, runner, tmp_path):
        (tmp_path / "modulo.py").write_text("x = 1")
        with patch("quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[]):
            result = runner.invoke(main, [str(tmp_path)])
        assert result.exit_code == 0

    def test_multiples_paths_aceptados(self, runner, tmp_path):
        pkg_a = tmp_path / "paquete_a"
        pkg_b = tmp_path / "paquete_b"
        pkg_a.mkdir()
        pkg_b.mkdir()
        (pkg_a / "modulo.py").write_text("x = 1")
        (pkg_b / "modulo.py").write_text("y = 2")
        with patch("quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[]):
            result = runner.invoke(main, [str(pkg_a), str(pkg_b)])
        assert result.exit_code == 0

    def test_sin_argumentos_usa_directorio_actual(self, runner, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "modulo.py").write_text("x = 1")
        with patch("quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[]):
            result = runner.invoke(main, [])
        assert result.exit_code == 0

    def test_path_inexistente_falla(self, runner):
        result = runner.invoke(main, ["/ruta/que/no/existe/"])
        assert result.exit_code != 0
