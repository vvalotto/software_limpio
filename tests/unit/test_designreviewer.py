"""
Tests unitarios para DesignReviewer.

Ticket: 1.3 — Refactorizar DesignReviewer como clase principal
"""

from pathlib import Path

from quality_agents.designreviewer import DesignReviewer
from quality_agents.designreviewer.agent import ReviewResult, ReviewSeverity


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
