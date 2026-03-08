"""
Tests de integración del CLI y formatter de ArchitectAnalyst.

Verifica el comportamiento end-to-end del comando `architectanalyst`:
- Salida Rich en modo text
- Salida JSON en modo json
- Exit code SIEMPRE 0 (ArchitectAnalyst nunca bloquea)
- Tendencias con y sin histórico

Ticket: 5.5 - Tests de integración CLI y formatter
Fecha: 2026-03-01
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from quality_agents.architectanalyst.agent import main
from quality_agents.architectanalyst.formatter import format_json, format_results
from quality_agents.architectanalyst.models import (
    ArchitectureResult,
    ArchitectureSeverity,
    MetricTrend,
)

# --- Helpers ---


def make_result(
    severity: ArchitectureSeverity,
    metric_name: str = "D",
    value: float = 0.6,
    trend: MetricTrend | None = None,
) -> ArchitectureResult:
    return ArchitectureResult(
        analyzer_name="TestAnalyzer",
        metric_name=metric_name,
        module_path=Path("src/modulo.py"),
        value=value,
        threshold=0.5,
        severity=severity,
        message="Métrica fuera de umbral",
        trend=trend,
    )


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
        (d / "modulo_a.py").write_text(PYTHON_LIMPIO)
        (d / "modulo_b.py").write_text(PYTHON_LIMPIO)
        yield d


# --- Tests del CLI ---


class TestArchitectAnalystCLI:
    def test_help_muestra_descripcion(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "ArchitectAnalyst" in result.output

    def test_formato_text_y_json_aceptados(self, runner, temp_python_file):
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[]
        ):
            result_text = runner.invoke(main, [str(temp_python_file), "--format", "text"])
            result_json = runner.invoke(main, [str(temp_python_file), "--format", "json"])

        assert result_text.exit_code == 0
        assert result_json.exit_code == 0

    def test_sprint_id_aceptado(self, runner, temp_python_file):
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[]
        ):
            result = runner.invoke(main, [str(temp_python_file), "--sprint-id", "sprint-12"])
        assert result.exit_code == 0

    def test_archivo_inexistente_falla(self, runner):
        result = runner.invoke(main, ["/ruta/que/no/existe/"])
        assert result.exit_code != 0

    def test_multiples_paths_aceptados(self, runner, tmp_path):
        """Dos directorios como argumentos separados deben aceptarse sin error."""
        pkg_a = tmp_path / "paquete_a"
        pkg_b = tmp_path / "paquete_b"
        pkg_a.mkdir()
        pkg_b.mkdir()
        (pkg_a / "modulo.py").write_text("class A: pass\n")
        (pkg_b / "modulo.py").write_text("class B: pass\n")
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[]
        ):
            result = runner.invoke(main, [str(pkg_a), str(pkg_b)])
        assert result.exit_code == 0

    def test_sin_argumentos_usa_directorio_actual(self, runner, tmp_path, monkeypatch):
        """Sin argumentos, analiza el directorio actual."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "modulo.py").write_text("x = 1")
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[]
        ):
            result = runner.invoke(main, [])
        assert result.exit_code == 0


# --- Tests de exit code — SIEMPRE 0 ---


class TestArchitectAnalystExitCode:
    def test_exit_code_0_sin_resultados(self, runner, temp_python_file):
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[]
        ):
            result = runner.invoke(main, [str(temp_python_file)])
        assert result.exit_code == 0

    def test_exit_code_0_con_warnings(self, runner, temp_python_file):
        warning = make_result(ArchitectureSeverity.WARNING)
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[warning]
        ):
            result = runner.invoke(main, [str(temp_python_file)])
        assert result.exit_code == 0

    def test_exit_code_0_con_critical(self, runner, temp_python_file):
        """ArchitectAnalyst nunca bloquea — exit code 0 incluso con CRITICAL."""
        critical = make_result(ArchitectureSeverity.CRITICAL)
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[critical]
        ):
            result = runner.invoke(main, [str(temp_python_file)])
        assert result.exit_code == 0

    def test_exit_code_0_con_mix_severidades(self, runner, temp_python_file):
        results = [
            make_result(ArchitectureSeverity.CRITICAL),
            make_result(ArchitectureSeverity.WARNING),
            make_result(ArchitectureSeverity.INFO),
        ]
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=results
        ):
            result = runner.invoke(main, [str(temp_python_file)])
        assert result.exit_code == 0


# --- Tests de salida text (Rich) ---


class TestArchitectAnalystTextOutput:
    def test_salida_text_sin_resultados(self, runner, temp_python_file):
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[]
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "text"])
        assert "ArchitectAnalyst" in result.output
        assert "Sin violaciones" in result.output

    def test_salida_text_con_critical_muestra_seccion_critica(self, runner, temp_python_file):
        critical = make_result(ArchitectureSeverity.CRITICAL, metric_name="DependencyCycles")
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[critical]
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "text"])
        assert "CRÍTICAS" in result.output or "CRITICAL" in result.output

    def test_salida_text_con_sprint_id_muestra_sprint(self, runner, temp_python_file):
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[]
        ):
            result = runner.invoke(
                main, [str(temp_python_file), "--format", "text", "--sprint-id", "sprint-42"]
            )
        assert "sprint-42" in result.output

    def test_salida_text_muestra_resumen(self, runner, temp_python_file):
        warning = make_result(ArchitectureSeverity.WARNING)
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[warning]
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "text"])
        assert "Resumen" in result.output

    def test_salida_text_sin_bloqueo_menciona_exit_code(self, runner, temp_python_file):
        critical = make_result(ArchitectureSeverity.CRITICAL)
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[critical]
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "text"])
        assert "exit code" in result.output or "siempre 0" in result.output


# --- Tests de salida JSON ---


class TestArchitectAnalystJsonOutput:
    def test_salida_json_valida(self, runner, temp_python_file):
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[]
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "summary" in data
        assert "results" in data
        assert "by_severity" in data

    def test_json_should_block_siempre_false(self, runner, temp_python_file):
        """ArchitectAnalyst: should_block siempre False, incluso con CRITICAL."""
        critical = make_result(ArchitectureSeverity.CRITICAL)
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[critical]
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "json"])
        data = json.loads(result.output)
        assert data["summary"]["should_block"] is False

    def test_json_incluye_sprint_id(self, runner, temp_python_file):
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[]
        ):
            result = runner.invoke(
                main, [str(temp_python_file), "--format", "json", "--sprint-id", "Q1-2026"]
            )
        data = json.loads(result.output)
        assert data["summary"]["sprint_id"] == "Q1-2026"

    def test_json_sin_historico_trend_available_false(self, runner, temp_python_file):
        result_sin_trend = make_result(ArchitectureSeverity.INFO, trend=None)
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run",
            return_value=[result_sin_trend],
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "json"])
        data = json.loads(result.output)
        assert data["summary"]["trend_available"] is False

    def test_json_con_historico_trend_available_true(self, runner, temp_python_file):
        result_con_trend = make_result(
            ArchitectureSeverity.WARNING, trend=MetricTrend.DEGRADING
        )
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run",
            return_value=[result_con_trend],
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "json"])
        data = json.loads(result.output)
        assert data["summary"]["trend_available"] is True

    def test_json_by_severity_agrupa_resultados(self, runner, temp_python_file):
        results = [
            make_result(ArchitectureSeverity.CRITICAL),
            make_result(ArchitectureSeverity.WARNING),
            make_result(ArchitectureSeverity.INFO),
        ]
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=results
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "json"])
        data = json.loads(result.output)
        assert len(data["by_severity"]["critical"]) == 1
        assert len(data["by_severity"]["warning"]) == 1
        assert len(data["by_severity"]["info"]) == 1

    def test_json_resultado_incluye_campos_requeridos(self, runner, temp_python_file):
        r = make_result(ArchitectureSeverity.WARNING, trend=MetricTrend.IMPROVING)
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[r]
        ):
            result = runner.invoke(main, [str(temp_python_file), "--format", "json"])
        data = json.loads(result.output)
        item = data["results"][0]
        assert "analyzer" in item
        assert "metric" in item
        assert "severity" in item
        assert "value" in item
        assert "trend" in item
        assert "trend_symbol" in item
        assert item["trend"] == "improving"

    def test_json_con_directorio(self, runner, temp_dir_with_python):
        with patch(
            "quality_agents.architectanalyst.agent.ArchitectAnalyst.run", return_value=[]
        ):
            result = runner.invoke(main, [str(temp_dir_with_python), "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["summary"]["total_results"] == 0


# --- Tests directos del formatter ---


class TestFormatResults:
    def test_format_results_sin_resultados(self, capsys):
        format_results([], elapsed=0.5, total_files=3, metrics_executed=5)
        captured = capsys.readouterr()
        assert "ArchitectAnalyst" in captured.out or captured.out == ""

    def test_format_results_con_critical(self):
        r = make_result(ArchitectureSeverity.CRITICAL, metric_name="DependencyCycles")
        # No lanza excepción
        format_results([r], elapsed=1.0, total_files=10, metrics_executed=5)

    def test_format_results_con_trend_degrading(self):
        r = make_result(ArchitectureSeverity.WARNING, trend=MetricTrend.DEGRADING)
        # No lanza excepción
        format_results([r], elapsed=0.5, total_files=5, metrics_executed=5)

    def test_format_results_con_sprint_id(self):
        r = make_result(ArchitectureSeverity.INFO)
        # No lanza excepción con sprint_id
        format_results([r], elapsed=0.3, total_files=2, metrics_executed=3, sprint_id="sprint-1")


class TestFormatJson:
    def test_json_estructura_basica(self):
        output = format_json([], elapsed=1.0, total_files=5, metrics_executed=3)
        data = json.loads(output)
        assert "summary" in data
        assert "results" in data
        assert "by_severity" in data

    def test_json_should_block_siempre_false(self):
        r = make_result(ArchitectureSeverity.CRITICAL)
        output = format_json([r])
        data = json.loads(output)
        assert data["summary"]["should_block"] is False

    def test_json_conteo_por_severidad(self):
        results = [
            make_result(ArchitectureSeverity.CRITICAL),
            make_result(ArchitectureSeverity.CRITICAL),
            make_result(ArchitectureSeverity.WARNING),
            make_result(ArchitectureSeverity.INFO),
        ]
        output = format_json(results)
        data = json.loads(output)
        assert data["summary"]["critical_violations"] == 2
        assert data["summary"]["warnings"] == 1
        assert data["summary"]["infos"] == 1
        assert data["summary"]["total_results"] == 4

    def test_json_trend_en_resultado(self):
        r = make_result(ArchitectureSeverity.WARNING, trend=MetricTrend.STABLE)
        output = format_json([r])
        data = json.loads(output)
        item = data["results"][0]
        assert item["trend"] == "stable"
        assert item["trend_symbol"] == "="

    def test_json_sin_trend_es_none(self):
        r = make_result(ArchitectureSeverity.INFO, trend=None)
        output = format_json([r])
        data = json.loads(output)
        item = data["results"][0]
        assert item["trend"] is None
        assert item["trend_symbol"] == "—"

    def test_json_sprint_id_en_summary(self):
        output = format_json([], sprint_id="sprint-7")
        data = json.loads(output)
        assert data["summary"]["sprint_id"] == "sprint-7"

    def test_json_sin_sprint_id_es_none(self):
        output = format_json([])
        data = json.loads(output)
        assert data["summary"]["sprint_id"] is None

    def test_json_trend_available_true_con_historico(self):
        r = make_result(ArchitectureSeverity.INFO, trend=MetricTrend.IMPROVING)
        output = format_json([r])
        data = json.loads(output)
        assert data["summary"]["trend_available"] is True

    def test_json_trend_available_false_sin_historico(self):
        r = make_result(ArchitectureSeverity.INFO, trend=None)
        output = format_json([r])
        data = json.loads(output)
        assert data["summary"]["trend_available"] is False

    def test_json_es_serializable(self):
        results = [
            make_result(ArchitectureSeverity.CRITICAL, trend=MetricTrend.DEGRADING),
            make_result(ArchitectureSeverity.WARNING, trend=MetricTrend.IMPROVING),
            make_result(ArchitectureSeverity.INFO, trend=None),
        ]
        output = format_json(results, elapsed=2.5, total_files=20, metrics_executed=5)
        # No lanza excepción y es JSON válido
        data = json.loads(output)
        assert len(data["results"]) == 3
