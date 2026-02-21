"""
Tests unitarios del formatter de DesignReviewer.

Ticket: 5.6 - Tests de integración del CLI
Fecha: 2026-02-21
"""

import json
from pathlib import Path

import pytest

from quality_agents.designreviewer.formatter import (
    _print_blocking_issues,
    _print_effort_summary,
    _print_header,
    _print_stats,
    _print_success,
    _print_summary,
    format_json,
    format_results,
)
from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity, SolidPrinciple


# --- Fixtures ---


def make_result(
    severity: ReviewSeverity = ReviewSeverity.WARNING,
    effort: float = 1.0,
    class_name: str | None = "MiClase",
    smell_type: str | None = None,
    solid_principle: SolidPrinciple | None = None,
) -> ReviewResult:
    return ReviewResult(
        analyzer_name="TestAnalyzer",
        severity=severity,
        current_value=10,
        threshold=5,
        message="Descripción del problema",
        file_path=Path("src/servicio.py"),
        class_name=class_name,
        estimated_effort=effort,
        smell_type=smell_type,
        solid_principle=solid_principle,
    )


@pytest.fixture
def critical_result():
    return make_result(severity=ReviewSeverity.CRITICAL, effort=2.0)


@pytest.fixture
def warning_result():
    return make_result(severity=ReviewSeverity.WARNING, effort=0.5)


@pytest.fixture
def info_result():
    return make_result(severity=ReviewSeverity.INFO, effort=0.0)


# --- Tests de format_results (salida Rich) ---


class TestFormatResults:
    def test_sin_resultados_muestra_exito(self, capsys):
        format_results([], elapsed=1.0, total_files=3, analyzers_executed=8)
        out = capsys.readouterr().out
        assert "DesignReviewer" in out
        assert "Sin violaciones" in out

    def test_con_criticals_muestra_blocking_issues(self, capsys, critical_result):
        format_results([critical_result], elapsed=1.0, total_files=1, analyzers_executed=8)
        out = capsys.readouterr().out
        assert "BLOCKING" in out
        assert "CRITICAL" in out.upper() or "Blocking" in out

    def test_con_warnings_muestra_advertencias(self, capsys, warning_result):
        format_results([warning_result], elapsed=1.0, total_files=1, analyzers_executed=8)
        out = capsys.readouterr().out
        assert "Advertencias" in out

    def test_muestra_estadisticas(self, capsys, warning_result):
        format_results([warning_result], elapsed=2.5, total_files=5, analyzers_executed=8)
        out = capsys.readouterr().out
        assert "5" in out   # total_files
        assert "8" in out   # analyzers_executed
        assert "2.50s" in out

    def test_muestra_esfuerzo_total(self, capsys):
        results = [
            make_result(severity=ReviewSeverity.CRITICAL, effort=2.0),
            make_result(severity=ReviewSeverity.WARNING, effort=1.5),
        ]
        format_results(results, elapsed=1.0, total_files=1, analyzers_executed=8)
        out = capsys.readouterr().out
        assert "Deuda Técnica" in out
        assert "3.5" in out   # esfuerzo total

    def test_sin_esfuerzo_no_muestra_panel(self, capsys):
        result = make_result(severity=ReviewSeverity.WARNING, effort=0.0)
        format_results([result], elapsed=1.0, total_files=1, analyzers_executed=8)
        out = capsys.readouterr().out
        assert "Deuda Técnica" not in out

    def test_mezcla_severidades(self, capsys, critical_result, warning_result, info_result):
        format_results(
            [critical_result, warning_result, info_result],
            elapsed=1.0,
            total_files=2,
            analyzers_executed=8,
        )
        out = capsys.readouterr().out
        assert "BLOCKING" in out
        assert "Advertencias" in out
        assert "Informativos" in out


# --- Tests de format_json ---


class TestFormatJson:
    def test_json_valido(self, warning_result):
        output = format_json([warning_result], elapsed=1.5, total_files=2, analyzers_executed=8)
        data = json.loads(output)
        assert "summary" in data
        assert "results" in data
        assert "by_severity" in data

    def test_summary_tiene_campos_requeridos(self, critical_result):
        output = format_json([critical_result], elapsed=2.0, total_files=3, analyzers_executed=8)
        summary = json.loads(output)["summary"]
        assert summary["total_files"] == 3
        assert summary["analyzers_executed"] == 8
        assert summary["blocking_issues"] == 1
        assert summary["warnings"] == 0
        assert summary["should_block"] is True

    def test_sin_criticos_should_block_false(self, warning_result):
        output = format_json([warning_result], elapsed=1.0, total_files=1, analyzers_executed=5)
        summary = json.loads(output)["summary"]
        assert summary["should_block"] is False
        assert summary["blocking_issues"] == 0
        assert summary["warnings"] == 1

    def test_estimated_effort_en_summary(self):
        results = [
            make_result(severity=ReviewSeverity.CRITICAL, effort=3.0),
            make_result(severity=ReviewSeverity.WARNING, effort=1.0),
        ]
        output = format_json(results, elapsed=1.0, total_files=1, analyzers_executed=8)
        summary = json.loads(output)["summary"]
        assert summary["estimated_effort_hours"]["total"] == 4.0
        assert summary["estimated_effort_hours"]["blocking"] == 3.0

    def test_by_severity_agrupa_correctamente(self, critical_result, warning_result):
        output = format_json(
            [critical_result, warning_result], elapsed=1.0, total_files=1, analyzers_executed=8
        )
        by_sev = json.loads(output)["by_severity"]
        assert len(by_sev["critical"]) == 1
        assert len(by_sev["warning"]) == 1
        assert len(by_sev["info"]) == 0

    def test_resultado_contiene_campos_completos(self, critical_result):
        output = format_json([critical_result], elapsed=1.0, total_files=1, analyzers_executed=8)
        result = json.loads(output)["results"][0]
        assert result["analyzer"] == "TestAnalyzer"
        assert result["severity"] == "critical"
        assert result["file"] == "src/servicio.py"
        assert result["class"] == "MiClase"
        assert result["current_value"] == 10
        assert result["threshold"] == 5
        assert result["estimated_effort_hours"] == 2.0

    def test_solid_principle_en_resultado(self):
        result = make_result(
            severity=ReviewSeverity.CRITICAL,
            solid_principle=SolidPrinciple.SRP,
            smell_type="GodObject",
        )
        output = format_json([result], elapsed=1.0, total_files=1, analyzers_executed=8)
        r = json.loads(output)["results"][0]
        assert r["solid_principle"] == "S"
        assert r["smell_type"] == "GodObject"

    def test_lista_vacia(self):
        output = format_json([], elapsed=0.5, total_files=0, analyzers_executed=8)
        data = json.loads(output)
        assert data["summary"]["total_issues"] == 0
        assert data["summary"]["should_block"] is False
        assert data["results"] == []

    def test_json_es_string_valido(self, warning_result):
        output = format_json([warning_result])
        assert isinstance(output, str)
        assert len(output) > 0
        json.loads(output)  # no debe lanzar excepción
