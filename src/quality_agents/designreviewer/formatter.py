"""
Formatter - Output formateado con Rich para DesignReviewer.

Muestra BLOCKING ISSUES (CRITICAL) separados de WARNINGS, con estimated_effort total.

Ticket: 5.2 - Formatter Rich
Ticket: 5.3 - estimated_effort total
Ticket: 5.4 - Salida JSON estructurada
Fecha: 2026-02-21
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity


def format_results(
    results: List[ReviewResult],
    elapsed: float,
    total_files: int = 0,
    analyzers_executed: int = 0,
) -> None:
    """
    Formatea y muestra resultados usando Rich.

    BLOCKING ISSUES (CRITICAL) se muestran en panel rojo separado de WARNINGS.
    Al final se muestra el estimated_effort total del changeset.

    Args:
        results: Lista de resultados del análisis de diseño.
        elapsed: Tiempo de ejecución en segundos.
        total_files: Número de archivos analizados.
        analyzers_executed: Número de analyzers ejecutados.
    """
    console = Console()

    _print_header(console)
    _print_stats(console, results, elapsed, total_files, analyzers_executed)

    if not results:
        _print_success(console)
        return

    criticals = [r for r in results if r.severity == ReviewSeverity.CRITICAL]
    warnings = [r for r in results if r.severity == ReviewSeverity.WARNING]
    infos = [r for r in results if r.severity == ReviewSeverity.INFO]

    if criticals:
        _print_blocking_issues(console, criticals)

    if warnings:
        _print_results_table(console, warnings, "Advertencias de Diseño", "yellow")

    if infos:
        _print_results_table(console, infos, "Informativos", "blue")

    _print_summary(console, criticals, warnings, infos)
    _print_effort_summary(console, results)


def _print_header(console: Console) -> None:
    title = Text()
    title.append("🔍  ", style="bold magenta")
    title.append("DesignReviewer", style="bold cyan")
    title.append(" - Análisis de Calidad de Diseño", style="dim")
    console.print(Panel(title, border_style="cyan", padding=(0, 2)))
    console.print()


def _print_stats(
    console: Console,
    results: List[ReviewResult],
    elapsed: float,
    total_files: int,
    analyzers_executed: int,
) -> None:
    stats = Table.grid(padding=(0, 2))
    stats.add_column(style="bold cyan")
    stats.add_column(style="white")

    stats.add_row("Archivos analizados:", str(total_files))
    stats.add_row("Analyzers ejecutados:", str(analyzers_executed))
    stats.add_row("Tiempo de ejecución:", f"{elapsed:.2f}s")
    stats.add_row("Resultados totales:", str(len(results)))

    console.print(stats)
    console.print()


def _print_success(console: Console) -> None:
    success_text = Text()
    success_text.append("✓ ", style="bold green")
    success_text.append("Sin violaciones de diseño detectadas", style="green")
    console.print(Panel(success_text, border_style="green", padding=(0, 2)))


def _print_blocking_issues(console: Console, criticals: List[ReviewResult]) -> None:
    """Imprime BLOCKING ISSUES en panel rojo destacado."""
    table = Table(
        title=f"🚫 BLOCKING ISSUES ({len(criticals)})",
        title_style="bold red",
        border_style="red",
        show_header=True,
        header_style="bold red",
    )

    table.add_column("Analyzer", style="cyan", no_wrap=True)
    table.add_column("Clase / Módulo", style="white", no_wrap=True)
    table.add_column("Problema", style="white", max_width=60)
    table.add_column("Valor", style="red", justify="right")
    table.add_column("Umbral", style="dim", justify="right")
    table.add_column("Esfuerzo", style="yellow", justify="right")

    for r in criticals:
        location = r.class_name or r.file_path.name
        effort = f"{r.estimated_effort:.1f}h" if r.estimated_effort else "-"
        table.add_row(
            r.analyzer_name,
            location,
            r.message,
            str(r.current_value),
            str(r.threshold),
            effort,
        )

    console.print(Panel(table, border_style="red", padding=(0, 1)))
    console.print()


def _print_results_table(
    console: Console,
    results: List[ReviewResult],
    title: str,
    color: str,
) -> None:
    table = Table(
        title=f"{title} ({len(results)})",
        title_style=f"bold {color}",
        border_style=color,
        show_header=True,
        header_style=f"bold {color}",
    )

    table.add_column("Analyzer", style="cyan", no_wrap=True)
    table.add_column("Clase / Módulo", style="white", no_wrap=True)
    table.add_column("Problema", style="white", max_width=70)
    table.add_column("Valor", justify="right")
    table.add_column("Umbral", style="dim", justify="right")
    table.add_column("Esfuerzo", style="yellow", justify="right")

    for r in results:
        location = r.class_name or r.file_path.name
        effort = f"{r.estimated_effort:.1f}h" if r.estimated_effort else "-"
        table.add_row(
            r.analyzer_name,
            location,
            r.message,
            str(r.current_value),
            str(r.threshold),
            effort,
        )

    console.print(table)
    console.print()


def _print_summary(
    console: Console,
    criticals: List[ReviewResult],
    warnings: List[ReviewResult],
    infos: List[ReviewResult],
) -> None:
    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="bold")
    summary.add_column(style="white")

    blocking_text = Text()
    blocking_text.append(str(len(criticals)), style="bold red" if criticals else "dim")
    blocking_text.append(" blocking issues (CRITICAL)", style="red" if criticals else "dim")

    warning_text = Text()
    warning_text.append(str(len(warnings)), style="bold yellow" if warnings else "dim")
    warning_text.append(" advertencias (WARNING)", style="yellow" if warnings else "dim")

    info_text = Text()
    info_text.append(str(len(infos)), style="bold blue" if infos else "dim")
    info_text.append(" informativos (INFO)", style="blue" if infos else "dim")

    summary.add_row("Resumen:", "")
    summary.add_row("", blocking_text)
    summary.add_row("", warning_text)
    summary.add_row("", info_text)

    border = "red" if criticals else "yellow" if warnings else "green"
    console.print(Panel(summary, border_style=border, title="Resumen Final", padding=(0, 2)))


def _print_effort_summary(console: Console, results: List[ReviewResult]) -> None:
    """Imprime estimated_effort total del changeset."""
    total_effort = sum(r.estimated_effort for r in results)
    if total_effort <= 0:
        return

    criticals = [r for r in results if r.severity == ReviewSeverity.CRITICAL]
    critical_effort = sum(r.estimated_effort for r in criticals)

    effort_text = Text()
    effort_text.append("Esfuerzo estimado de refactoring:\n", style="bold")
    effort_text.append(f"  Blocking issues: ", style="red")
    effort_text.append(f"{critical_effort:.1f}h\n", style="bold red")
    effort_text.append(f"  Total del changeset: ", style="cyan")
    effort_text.append(f"{total_effort:.1f}h", style="bold cyan")

    console.print()
    console.print(Panel(effort_text, border_style="cyan", title="⏱  Deuda Técnica", padding=(0, 2)))


def format_json(
    results: List[ReviewResult],
    elapsed: float = 0.0,
    total_files: int = 0,
    analyzers_executed: int = 0,
) -> str:
    """
    Formatea resultados en JSON estructurado.

    Args:
        results: Lista de resultados del análisis.
        elapsed: Tiempo de ejecución en segundos.
        total_files: Número de archivos analizados.
        analyzers_executed: Número de analyzers ejecutados.

    Returns:
        String con JSON formateado (pretty-printed).
    """
    criticals = [r for r in results if r.severity == ReviewSeverity.CRITICAL]
    warnings = [r for r in results if r.severity == ReviewSeverity.WARNING]
    infos = [r for r in results if r.severity == ReviewSeverity.INFO]

    total_effort = sum(r.estimated_effort for r in results)
    critical_effort = sum(r.estimated_effort for r in criticals)

    output: Dict[str, Any] = {
        "summary": {
            "total_files": total_files,
            "analyzers_executed": analyzers_executed,
            "elapsed_seconds": round(elapsed, 2),
            "timestamp": datetime.now().isoformat(),
            "total_issues": len(results),
            "blocking_issues": len(criticals),
            "warnings": len(warnings),
            "infos": len(infos),
            "should_block": len(criticals) > 0,
            "estimated_effort_hours": {
                "blocking": round(critical_effort, 1),
                "total": round(total_effort, 1),
            },
        },
        "results": [_result_to_dict(r) for r in results],
        "by_severity": {
            "critical": [_result_to_dict(r) for r in criticals],
            "warning": [_result_to_dict(r) for r in warnings],
            "info": [_result_to_dict(r) for r in infos],
        },
    }

    return json.dumps(output, indent=2, ensure_ascii=False)


def _result_to_dict(r: ReviewResult) -> Dict[str, Any]:
    return {
        "analyzer": r.analyzer_name,
        "severity": r.severity.value,
        "message": r.message,
        "file": str(r.file_path),
        "class": r.class_name,
        "current_value": r.current_value,
        "threshold": r.threshold,
        "estimated_effort_hours": r.estimated_effort,
        "solid_principle": r.solid_principle.value if r.solid_principle else None,
        "smell_type": r.smell_type,
        "suggestion": r.suggestion,
    }
