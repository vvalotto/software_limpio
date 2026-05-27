"""
CoverageAnalyzer — Cobertura de tests en el reporte de ArchitectAnalyst.

Lee el archivo coverage.json generado por `pytest --cov --cov-report=json`
y reporta el porcentaje de líneas cubiertas.

Comportamiento:
  - Archivo no encontrado  → WARNING (sin datos de cobertura)
  - Archivo inválido       → WARNING (no se pudo leer)
  - Cobertura < umbral     → WARNING
  - Cobertura >= umbral    → INFO

Umbrales en ArchitectAnalystConfig:
  coverage_report_path (default: "coverage.json") → ruta relativa al project_path
  min_coverage         (default: 80.0)            → porcentaje mínimo esperado

Ticket: Issue #49
Fecha: 2026-05-27
"""

import json
from pathlib import Path
from typing import Any, List

from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity
from quality_agents.architectanalyst.orchestrator import ProjectMetric


class CoverageAnalyzer(ProjectMetric):
    """
    Reporta la cobertura de tests leyendo coverage.json.

    WARNING si no se encuentra el archivo o si cobertura < min_coverage.
    INFO si la cobertura supera el umbral.
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "CoverageAnalyzer"

    @property
    def category(self) -> str:
        return "quality"

    @property
    def estimated_duration(self) -> float:
        return 1.0

    @property
    def priority(self) -> int:
        return 11

    def should_run(self, config: Any) -> bool:
        self._config = config
        if config and hasattr(config, "checks"):
            if not getattr(config.checks, "coverage", True):
                return False
        return True

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        config = self._config
        min_cov = getattr(config, "min_coverage", 80.0) if config else 80.0
        report_path_str = (
            getattr(config, "coverage_report_path", "coverage.json") if config else "coverage.json"
        )

        report_path = project_path / report_path_str

        if not report_path.exists():
            return [ArchitectureResult(
                analyzer_name=self.name,
                metric_name="coverage",
                module_path=Path("."),
                value=0.0,
                threshold=min_cov,
                severity=ArchitectureSeverity.WARNING,
                message=(
                    f"No se encontró el archivo de cobertura '{report_path_str}'. "
                    f"Generalo con: pytest --cov --cov-report=json"
                ),
            )]

        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
            percent = float(data["totals"]["percent_covered"])
        except (json.JSONDecodeError, KeyError, OSError, TypeError, ValueError):
            return [ArchitectureResult(
                analyzer_name=self.name,
                metric_name="coverage",
                module_path=Path("."),
                value=0.0,
                threshold=min_cov,
                severity=ArchitectureSeverity.WARNING,
                message=(
                    f"No se pudo leer el archivo de cobertura '{report_path_str}'. "
                    f"Verificá que sea un JSON válido generado por coverage.py."
                ),
            )]

        severity = (
            ArchitectureSeverity.WARNING if percent < min_cov else ArchitectureSeverity.INFO
        )
        comparison = "por debajo del" if percent < min_cov else "dentro del"
        return [ArchitectureResult(
            analyzer_name=self.name,
            metric_name="coverage",
            module_path=Path("."),
            value=round(percent, 1),
            threshold=min_cov,
            severity=severity,
            message=(
                f"Cobertura de tests: {percent:.1f}% "
                f"({comparison} umbral mínimo de {min_cov}%)."
            ),
        )]
