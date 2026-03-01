"""
Formatter - Output formateado con Rich para ArchitectAnalyst.

Muestra métricas de Martin con columna de tendencia, y sección CRITICAL separada
para ciclos de dependencias y violaciones de capas.

A diferencia de DesignReviewer, ArchitectAnalyst nunca bloquea — exit code siempre 0.

Ticket: 5.2 - Formatter Rich
Ticket: 5.3 - Salida JSON estructurada
Fecha: 2026-03-01
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from quality_agents.architectanalyst.models import (
    ArchitectureResult,
    ArchitectureSeverity,
    MetricTrend,
)

_TREND_STYLE = {
    MetricTrend.IMPROVING: "bold green",
    MetricTrend.STABLE: "dim",
    MetricTrend.DEGRADING: "bold red",
}


def format_results(
    results: List[ArchitectureResult],
    elapsed: float,
    total_files: int = 0,
    metrics_executed: int = 0,
    sprint_id: str | None = None,
) -> None:
    """
    Formatea y muestra resultados usando Rich.

    Los resultados CRITICAL (ciclos, violaciones de capas) se muestran en sección
    separada destacada en rojo. Las métricas de Martin se muestran en tabla con
    columna de tendencia respecto al snapshot anterior.

    Args:
        results: Lista de resultados del análisis arquitectónico.
        elapsed: Tiempo de ejecución en segundos.
        total_files: Número de archivos analizados.
        metrics_executed: Número de métricas ejecutadas.
        sprint_id: Identificador del sprint (opcional).
    """
    console = Console()

    _print_header(console, sprint_id)
    _print_stats(console, results, elapsed, total_files, metrics_executed)

    if not results:
        _print_success(console)
        return

    criticals = [r for r in results if r.severity == ArchitectureSeverity.CRITICAL]
    warnings = [r for r in results if r.severity == ArchitectureSeverity.WARNING]
    infos = [r for r in results if r.severity == ArchitectureSeverity.INFO]

    if criticals:
        _print_critical_issues(console, criticals)

    if warnings or infos:
        _print_metrics_table(console, warnings + infos)

    _print_summary(console, criticals, warnings, infos)


def _print_header(console: Console, sprint_id: str | None) -> None:
    title = Text()
    title.append("🏛  ", style="bold magenta")
    title.append("ArchitectAnalyst", style="bold cyan")
    title.append(" - Análisis Arquitectónico de Fin de Sprint", style="dim")
    if sprint_id:
        title.append(f"  [{sprint_id}]", style="bold yellow")
    console.print(Panel(title, border_style="cyan", padding=(0, 2)))
    console.print()


def _print_stats(
    console: Console,
    results: List[ArchitectureResult],
    elapsed: float,
    total_files: int,
    metrics_executed: int,
) -> None:
    has_trend = any(r.trend is not None for r in results)

    stats = Table.grid(padding=(0, 2))
    stats.add_column(style="bold cyan")
    stats.add_column(style="white")

    stats.add_row("Archivos analizados:", str(total_files))
    stats.add_row("Métricas ejecutadas:", str(metrics_executed))
    stats.add_row("Tiempo de ejecución:", f"{elapsed:.2f}s")
    stats.add_row("Resultados totales:", str(len(results)))
    stats.add_row("Tendencias:", "disponibles ↑↓=" if has_trend else "sin histórico (primer análisis)")

    console.print(stats)
    console.print()


def _print_success(console: Console) -> None:
    success_text = Text()
    success_text.append("✓ ", style="bold green")
    success_text.append("Sin violaciones arquitectónicas detectadas", style="green")
    console.print(Panel(success_text, border_style="green", padding=(0, 2)))


def _print_critical_issues(console: Console, criticals: List[ArchitectureResult]) -> None:
    """Imprime violaciones CRITICAL (ciclos, capas) con regla roja destacada."""
    console.print(Rule(f"🚫  VIOLACIONES CRÍTICAS ({len(criticals)})", style="bold red"))
    console.print()

    table = Table(
        border_style="red",
        show_header=True,
        header_style="bold red",
        expand=True,
    )

    table.add_column("Métrica", style="cyan", no_wrap=True, min_width=12)
    table.add_column("Módulo", style="white", no_wrap=True, min_width=20)
    table.add_column("Problema", style="white", ratio=1, overflow="ellipsis")
    table.add_column("Trend", justify="center", no_wrap=True, min_width=5)

    for r in criticals:
        trend_text = _trend_text(r)
        table.add_row(
            r.metric_name,
            str(r.module_path),
            r.message,
            trend_text,
        )

    console.print(table)
    console.print()


def _print_metrics_table(console: Console, results: List[ArchitectureResult]) -> None:
    """Tabla principal con métricas de Martin (WARNING e INFO)."""
    warnings = [r for r in results if r.severity == ArchitectureSeverity.WARNING]
    infos = [r for r in results if r.severity == ArchitectureSeverity.INFO]
    title_parts = []
    if warnings:
        title_parts.append(f"{len(warnings)} advertencias")
    if infos:
        title_parts.append(f"{len(infos)} informativos")
    title = "Métricas Arquitectónicas — " + " + ".join(title_parts)

    color = "yellow" if warnings else "blue"

    table = Table(
        title=title,
        title_style=f"bold {color}",
        border_style=color,
        show_header=True,
        header_style=f"bold {color}",
        expand=True,
    )

    table.add_column("Métrica", style="cyan", no_wrap=True, min_width=10)
    table.add_column("Módulo", style="white", no_wrap=True, min_width=20)
    table.add_column("Valor", justify="right", no_wrap=True, min_width=6)
    table.add_column("Umbral", justify="right", no_wrap=True, min_width=6)
    table.add_column("Trend", justify="center", no_wrap=True, min_width=5)
    table.add_column("Severidad", justify="center", no_wrap=True, min_width=10)

    for r in results:
        threshold_str = f"{r.threshold:.2f}" if r.threshold is not None else "—"
        severity_text = _severity_text(r)
        trend_text = _trend_text(r)
        table.add_row(
            r.metric_name,
            str(r.module_path),
            f"{r.value:.3f}",
            threshold_str,
            trend_text,
            severity_text,
        )

    console.print(table)
    console.print()


def _trend_text(r: ArchitectureResult) -> Text:
    """Genera texto Rich con símbolo y color de tendencia."""
    if r.trend is None:
        return Text("—", style="dim")
    symbol = r.trend.symbol
    style = _TREND_STYLE.get(r.trend, "white")
    return Text(symbol, style=style)


def _severity_text(r: ArchitectureResult) -> Text:
    styles = {
        ArchitectureSeverity.CRITICAL: "bold red",
        ArchitectureSeverity.WARNING: "bold yellow",
        ArchitectureSeverity.INFO: "dim blue",
    }
    style = styles.get(r.severity, "white")
    return Text(r.severity.value.upper(), style=style)


def _print_summary(
    console: Console,
    criticals: List[ArchitectureResult],
    warnings: List[ArchitectureResult],
    infos: List[ArchitectureResult],
) -> None:
    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="bold")
    summary.add_column(style="white")

    critical_text = Text()
    critical_text.append(str(len(criticals)), style="bold red" if criticals else "dim")
    critical_text.append(" violaciones críticas (CRITICAL)", style="red" if criticals else "dim")

    warning_text = Text()
    warning_text.append(str(len(warnings)), style="bold yellow" if warnings else "dim")
    warning_text.append(" advertencias (WARNING)", style="yellow" if warnings else "dim")

    info_text = Text()
    info_text.append(str(len(infos)), style="bold blue" if infos else "dim")
    info_text.append(" informativos (INFO)", style="blue" if infos else "dim")

    note_text = Text()
    note_text.append("ArchitectAnalyst no bloquea — exit code siempre 0", style="dim italic")

    summary.add_row("Resumen:", "")
    summary.add_row("", critical_text)
    summary.add_row("", warning_text)
    summary.add_row("", info_text)
    summary.add_row("", note_text)

    border = "red" if criticals else "yellow" if warnings else "green"
    console.print(Panel(summary, border_style=border, title="Resumen Final", padding=(0, 2)))


def format_json(
    results: List[ArchitectureResult],
    elapsed: float = 0.0,
    total_files: int = 0,
    metrics_executed: int = 0,
    sprint_id: str | None = None,
) -> str:
    """
    Formatea resultados en JSON estructurado.

    Args:
        results: Lista de resultados del análisis.
        elapsed: Tiempo de ejecución en segundos.
        total_files: Número de archivos analizados.
        metrics_executed: Número de métricas ejecutadas.
        sprint_id: Identificador del sprint (opcional).

    Returns:
        String con JSON formateado (pretty-printed).
    """
    criticals = [r for r in results if r.severity == ArchitectureSeverity.CRITICAL]
    warnings = [r for r in results if r.severity == ArchitectureSeverity.WARNING]
    infos = [r for r in results if r.severity == ArchitectureSeverity.INFO]
    has_trend = any(r.trend is not None for r in results)

    output: Dict[str, Any] = {
        "summary": {
            "sprint_id": sprint_id,
            "total_files": total_files,
            "metrics_executed": metrics_executed,
            "elapsed_seconds": round(elapsed, 2),
            "timestamp": datetime.now().isoformat(),
            "total_results": len(results),
            "critical_violations": len(criticals),
            "warnings": len(warnings),
            "infos": len(infos),
            "trend_available": has_trend,
            "should_block": False,  # ArchitectAnalyst nunca bloquea
        },
        "results": [_result_to_dict(r) for r in results],
        "by_severity": {
            "critical": [_result_to_dict(r) for r in criticals],
            "warning": [_result_to_dict(r) for r in warnings],
            "info": [_result_to_dict(r) for r in infos],
        },
    }

    return json.dumps(output, indent=2, ensure_ascii=False)


def _result_to_dict(r: ArchitectureResult) -> Dict[str, Any]:
    return {
        "analyzer": r.analyzer_name,
        "metric": r.metric_name,
        "severity": r.severity.value,
        "message": r.message,
        "module": str(r.module_path),
        "value": r.value,
        "threshold": r.threshold,
        "trend": r.trend.value if r.trend is not None else None,
        "trend_symbol": r.trend_symbol(),
    }
