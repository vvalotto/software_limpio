"""
Formatter - Output formateado con Rich

Fecha de creación: 2026-02-04
Ticket: 4.1 - Implementar formatter con Rich
Ticket: 4.2 - Agregar modo JSON
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from quality_agents.codeguard.agent import CheckResult, Severity


def format_results(
    results: List[CheckResult],
    elapsed: float,
    total_files: int = 0,
    checks_executed: int = 0,
) -> None:
    """
    Formatea y muestra resultados usando Rich.

    Args:
        results: Lista de resultados de verificación
        elapsed: Tiempo de ejecución en segundos
        total_files: Número total de archivos analizados
        checks_executed: Número de checks ejecutados

    Example:
        >>> results = [CheckResult(...), CheckResult(...)]
        >>> format_results(results, elapsed=2.5, total_files=10, checks_executed=6)
    """
    console = Console()

    # Header con logo/título
    _print_header(console)

    # Estadísticas generales
    _print_stats(console, results, elapsed, total_files, checks_executed)

    # Si no hay resultados, mostrar mensaje de éxito y terminar
    if not results:
        _print_success(console)
        return

    # Agrupar por severidad (para resumen)
    errors = [r for r in results if r.severity == Severity.ERROR]
    warnings = [r for r in results if r.severity == Severity.WARNING]
    infos = [r for r in results if r.severity == Severity.INFO]

    # Mostrar resultados agrupados por paquete
    by_package = _group_by_package(results)
    for pkg_name in sorted(by_package.keys()):
        pkg_results = by_package[pkg_name]
        console.print(Rule(f"📦  {pkg_name}  ({len(pkg_results)} issues)", style="cyan"))
        console.print()

        pkg_errors = [r for r in pkg_results if r.severity == Severity.ERROR]
        pkg_warnings = [r for r in pkg_results if r.severity == Severity.WARNING]
        pkg_infos = [r for r in pkg_results if r.severity == Severity.INFO]

        if pkg_errors:
            _print_results_table(console, pkg_errors, "Errores", "red")
        if pkg_warnings:
            _print_results_table(console, pkg_warnings, "Advertencias", "yellow")
        if pkg_infos:
            _print_results_table(console, pkg_infos, "Informativos", "blue")

    # Summary final
    _print_summary(console, errors, warnings, infos)


def _package_name(file_path: Optional[str]) -> str:
    """Extrae el nombre del paquete (directorio padre) del file_path."""
    if not file_path:
        return "(sin archivo)"
    parent = Path(file_path).parent
    return parent.name or "."


def _group_by_package(results: List[CheckResult]) -> Dict[str, List[CheckResult]]:
    """Agrupa resultados por paquete (directorio padre del archivo)."""
    groups: Dict[str, List[CheckResult]] = defaultdict(list)
    for r in results:
        groups[_package_name(r.file_path)].append(r)
    return dict(groups)


def _print_header(console: Console) -> None:
    """Imprime header con título."""
    title = Text()
    title.append("🛡️  ", style="bold blue")
    title.append("CodeGuard", style="bold cyan")
    title.append(" - Control de Calidad Automatizado", style="dim")

    console.print(Panel(title, border_style="cyan", padding=(0, 2)))
    console.print()


def _print_stats(
    console: Console,
    results: List[CheckResult],
    elapsed: float,
    total_files: int,
    checks_executed: int,
) -> None:
    """Imprime estadísticas generales."""
    stats = Table.grid(padding=(0, 2))
    stats.add_column(style="bold cyan")
    stats.add_column(style="white")

    stats.add_row("Archivos analizados:", f"{total_files}")
    stats.add_row("Checks ejecutados:", f"{checks_executed}")
    stats.add_row("Tiempo de ejecución:", f"{elapsed:.2f}s")
    stats.add_row("Resultados totales:", f"{len(results)}")

    console.print(stats)
    console.print()


def _print_success(console: Console) -> None:
    """Imprime mensaje de éxito cuando no hay problemas."""
    success_text = Text()
    success_text.append("✓ ", style="bold green")
    success_text.append("No se encontraron problemas", style="green")

    console.print(Panel(success_text, border_style="green", padding=(0, 2)))


def _print_results_table(
    console: Console,
    results: List[CheckResult],
    title: str,
    color: str,
) -> None:
    """
    Imprime tabla de resultados para una severidad específica.

    Args:
        console: Consola Rich
        results: Lista de resultados de esa severidad
        title: Título de la tabla
        color: Color para el borde y título
    """
    table = Table(
        title=f"{title} ({len(results)})",
        title_style=f"bold {color}",
        border_style=color,
        show_header=True,
        header_style=f"bold {color}",
    )

    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Ubicación", style="white")
    table.add_column("Mensaje", style="white", max_width=80)

    for result in results:
        # Ubicación
        if result.line_number:
            location = f"{result.file_path}:{result.line_number}"
        else:
            location = result.file_path or "-"

        # Mensaje (truncar si es muy largo)
        message = result.message
        if len(message) > 100:
            message = message[:97] + "..."

        table.add_row(
            result.check_name,
            location,
            message,
        )

    console.print(table)
    console.print()


def _print_summary(
    console: Console,
    errors: List[CheckResult],
    warnings: List[CheckResult],
    infos: List[CheckResult],
) -> None:
    """Imprime resumen final con contadores."""
    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="bold")
    summary.add_column(style="white")

    # Contadores con colores
    error_text = Text()
    error_text.append(f"{len(errors)}", style="bold red" if errors else "dim")
    error_text.append(" errores", style="red" if errors else "dim")

    warning_text = Text()
    warning_text.append(f"{len(warnings)}", style="bold yellow" if warnings else "dim")
    warning_text.append(" advertencias", style="yellow" if warnings else "dim")

    info_text = Text()
    info_text.append(f"{len(infos)}", style="bold blue" if infos else "dim")
    info_text.append(" informativos", style="blue" if infos else "dim")

    summary.add_row("Resumen:", "")
    summary.add_row("", error_text)
    summary.add_row("", warning_text)
    summary.add_row("", info_text)

    console.print(Panel(summary, border_style="cyan", title="Resumen Final", padding=(0, 2)))

    # Sugerencias
    _print_suggestions(console, errors, warnings)


def _print_suggestions(
    console: Console,
    errors: List[CheckResult],
    warnings: List[CheckResult],
) -> None:
    """Imprime sugerencias según los resultados."""
    if not errors and not warnings:
        return

    console.print()
    suggestions = []

    if errors:
        suggestions.append("• [bold red]Errores detectados[/]: Revisa y corrige antes de commitear")

    if warnings:
        suggestions.append("• [bold yellow]Advertencias encontradas[/]: Considera resolverlas para mejorar la calidad")

    # Sugerencias específicas comunes
    check_names = {r.check_name for r in errors + warnings}

    if "PEP8" in check_names:
        suggestions.append("• [cyan]PEP8[/]: Ejecuta [bold]black .[/] para auto-formatear")

    if "UnusedImports" in check_names:
        suggestions.append("• [cyan]Imports[/]: Ejecuta [bold]autoflake --remove-unused-variables .[/] para limpiar")

    if "Complexity" in check_names:
        suggestions.append("• [cyan]Complejidad[/]: Refactoriza funciones complejas en funciones más pequeñas")

    if "Security" in check_names:
        suggestions.append("• [red]Seguridad[/]: [bold]¡CRÍTICO![/] Revisa inmediatamente las vulnerabilidades")

    if suggestions:
        console.print(Panel(
            "\n".join(suggestions),
            title="💡 Sugerencias",
            border_style="yellow",
            padding=(1, 2),
        ))


def format_json(
    results: List[CheckResult],
    elapsed: float = 0.0,
    total_files: int = 0,
    checks_executed: int = 0,
) -> str:
    """
    Formatea resultados en formato JSON estructurado.

    Args:
        results: Lista de resultados de verificación
        elapsed: Tiempo de ejecución en segundos
        total_files: Número total de archivos analizados
        checks_executed: Número de checks ejecutados

    Returns:
        String con JSON formateado (pretty-printed)

    Example:
        >>> results = [CheckResult(...), CheckResult(...)]
        >>> json_output = format_json(results, elapsed=2.5, total_files=10, checks_executed=6)
        >>> print(json_output)
    """
    # Agrupar por severidad para estadísticas
    errors = [r for r in results if r.severity == Severity.ERROR]
    warnings = [r for r in results if r.severity == Severity.WARNING]
    infos = [r for r in results if r.severity == Severity.INFO]

    # Estructura JSON mejorada
    output: Dict[str, Any] = {
        "summary": {
            "total_files": total_files,
            "checks_executed": checks_executed,
            "elapsed_seconds": round(elapsed, 2),
            "timestamp": datetime.now().isoformat(),
            "total_issues": len(results),
            "errors": len(errors),
            "warnings": len(warnings),
            "infos": len(infos),
        },
        "results": [
            {
                "check": r.check_name,
                "severity": r.severity.value,
                "message": r.message,
                "file": r.file_path,
                "line": r.line_number,
            }
            for r in results
        ],
    }

    def _r_to_dict(r: CheckResult) -> Dict[str, Any]:
        return {
            "check": r.check_name,
            "severity": r.severity.value,
            "message": r.message,
            "file": r.file_path,
            "line": r.line_number,
        }

    # Si hay resultados, agregar agrupación por severidad y por paquete
    if results:
        output["by_severity"] = {
            "errors": [_r_to_dict(r) for r in errors],
            "warnings": [_r_to_dict(r) for r in warnings],
            "infos": [_r_to_dict(r) for r in infos],
        }

        by_pkg = _group_by_package(results)
        output["by_package"] = {
            pkg: [_r_to_dict(r) for r in pkg_results]
            for pkg, pkg_results in sorted(by_pkg.items())
        }

    return json.dumps(output, indent=2, ensure_ascii=False)
