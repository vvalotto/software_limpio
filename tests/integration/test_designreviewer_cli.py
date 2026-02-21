"""
Tests de integración del CLI de DesignReviewer.

Verifica el comportamiento end-to-end del comando `designreviewer`:
- Salida Rich en modo text
- Salida JSON en modo json
- Exit code 0 sin CRITICAL, 1 con CRITICAL

Ticket: 5.6 - Tests de integración del CLI
Fecha: 2026-02-21
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from quality_agents.designreviewer.agent import main
from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity

# --- Fixtures ---

PYTHON_LIMPIO = "# Archivo sin problemas\ndef suma(a, b):\n    return a + b\n"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def temp_python_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(PYTHON_LIMPIO)
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def temp_dir_with_python():
    with tempfile.TemporaryDirectory() as tmpdir:
        d = Path(tmpdir)
        (d / "servicio.py").write_text(PYTHON_LIMPIO)
        (d / "modelo.py").write_text(PYTHON_LIMPIO)
        yield d


def make_result(severity: ReviewSeverity, effort: float = 1.0) -> ReviewResult:
    return ReviewResult(
        analyzer_name="TestAnalyzer",
        severity=severity,
        current_value=10,
        threshold=5,
        message="Problema de diseño detectado",
        file_path=Path("src/servicio.py"),
        class_name="MiServicio",
        estimated_effort=effort,
    )


# --- Tests básicos del CLI ---


class TestDesignReviewerCLI:
    def test_help_muestra_descripcion(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "DesignReviewer" in result.output
        assert "CRITICAL" in result.output

    def test_formato_valido_text_y_json(self, runner, temp_python_file):
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[]
        ):
            result_text = runner.invoke(main, [str(temp_python_file), "--format", "text"])
            result_json = runner.invoke(main, [str(temp_python_file), "--format", "json"])

        assert result_text.exit_code == 0
        assert result_json.exit_code == 0

    def test_archivo_inexistente_falla(self, runner):
        result = runner.invoke(main, ["/ruta/que/no/existe/archivo.py"])
        assert result.exit_code != 0


# --- Tests de exit code ---


class TestDesignReviewerExitCode:
    def test_exit_code_0_sin_resultados(self, runner, temp_python_file):
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[]
        ):
            result = runner.invoke(main, [str(temp_python_file)])
        assert result.exit_code == 0

    def test_exit_code_0_con_solo_warnings(self, runner, temp_python_file):
        warning = make_result(ReviewSeverity.WARNING)
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[warning]
        ):
            result = runner.invoke(main, [str(temp_python_file)])
        assert result.exit_code == 0

    def test_exit_code_1_con_critical(self, runner, temp_python_file):
        critical = make_result(ReviewSeverity.CRITICAL)
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[critical]
        ):
            result = runner.invoke(main, [str(temp_python_file)])
        assert result.exit_code == 1

    def test_exit_code_1_con_mix_critical_y_warning(self, runner, temp_python_file):
        results = [
            make_result(ReviewSeverity.CRITICAL),
            make_result(ReviewSeverity.WARNING),
        ]
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=results
        ):
            result = runner.invoke(main, [str(temp_python_file)])
        assert result.exit_code == 1


# --- Tests de salida text (Rich) ---


class TestDesignReviewerTextOutput:
    def test_salida_text_sin_problemas(self, runner, temp_python_file):
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[]
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "text"])
        assert "DesignReviewer" in result.output
        assert "Sin violaciones" in result.output

    def test_salida_text_con_criticals_muestra_blocking(self, runner, temp_python_file):
        critical = make_result(ReviewSeverity.CRITICAL)
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[critical]
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "text"])
        assert "BLOCKING" in result.output

    def test_salida_text_con_effort_muestra_deuda(self, runner, temp_python_file):
        results = [
            make_result(ReviewSeverity.CRITICAL, effort=2.0),
            make_result(ReviewSeverity.WARNING, effort=1.0),
        ]
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=results
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "text"])
        assert "Deuda Técnica" in result.output

    def test_salida_text_muestra_estadisticas(self, runner, temp_dir_with_python):
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[]
        ):
            result = runner.invoke(main, [str(temp_dir_with_python), "--format", "text"])
        # Debe mostrar estadísticas de archivos
        assert result.exit_code == 0
        assert "DesignReviewer" in result.output


# --- Tests de salida JSON ---


class TestDesignReviewerJsonOutput:
    def test_salida_json_valida(self, runner, temp_python_file):
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[]
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "summary" in data
        assert "results" in data

    def test_json_sin_criticos_should_block_false(self, runner, temp_python_file):
        warning = make_result(ReviewSeverity.WARNING)
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[warning]
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "json"])
        data = json.loads(result.output)
        assert data["summary"]["should_block"] is False

    def test_json_con_criticals_should_block_true(self, runner, temp_python_file):
        critical = make_result(ReviewSeverity.CRITICAL)
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[critical]
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "json"])
        data = json.loads(result.output)
        assert data["summary"]["should_block"] is True
        assert data["summary"]["blocking_issues"] == 1

    def test_json_incluye_estimated_effort(self, runner, temp_python_file):
        results = [make_result(ReviewSeverity.CRITICAL, effort=3.0)]
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=results
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "json"])
        data = json.loads(result.output)
        effort = data["summary"]["estimated_effort_hours"]
        assert effort["total"] == 3.0
        assert effort["blocking"] == 3.0

    def test_json_by_severity_agrupa_resultados(self, runner, temp_python_file):
        results = [
            make_result(ReviewSeverity.CRITICAL),
            make_result(ReviewSeverity.WARNING),
            make_result(ReviewSeverity.INFO),
        ]
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=results
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "json"])
        data = json.loads(result.output)
        assert len(data["by_severity"]["critical"]) == 1
        assert len(data["by_severity"]["warning"]) == 1
        assert len(data["by_severity"]["info"]) == 1

    def test_json_con_directorio(self, runner, temp_dir_with_python):
        with patch(
            "quality_agents.designreviewer.agent.DesignReviewer.run", return_value=[]
        ):
            result = runner.invoke(main, [str(temp_dir_with_python), "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["summary"]["total_issues"] == 0
