"""
Utilidades de reporting compartidas.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table


class Severity(Enum):
    """Severidad de resultados."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


SEVERITY_COLORS = {
    Severity.INFO: "blue",
    Severity.WARNING: "yellow",
    Severity.ERROR: "red",
    Severity.CRITICAL: "bold red",
}


def format_result(
    check_name: str,
    severity: Severity,
    message: str,
    file_path: Optional[str] = None,
    line_number: Optional[int] = None
) -> str:
    """
    Formatea un resultado para salida en consola.

    Args:
        check_name: Nombre de la verificación
        severity: Severidad del resultado
        message: Mensaje descriptivo
        file_path: Ruta al archivo (opcional)
        line_number: Número de línea (opcional)

    Returns:
        Resultado formateado
    """
    location = ""
    if file_path:
        location = f" en {file_path}"
        if line_number:
            location += f":{line_number}"

    return f"[{severity.value.upper()}] {check_name}{location}: {message}"


def generate_summary(results: List[Dict[str, Any]]) -> str:
    """
    Genera resumen de resultados.

    Args:
        results: Lista de resultados

    Returns:
        Resumen textual
    """
    if not results:
        return "No se encontraron problemas."

    counts = dict.fromkeys(Severity, 0)
    for r in results:
        severity = r.get("severity", Severity.INFO)
        if isinstance(severity, str):
            severity = Severity(severity)
        counts[severity] += 1

    lines = ["Resumen de análisis:"]
    for severity, count in counts.items():
        if count > 0:
            lines.append(f"  - {severity.value.upper()}: {count}")

    return "\n".join(lines)


def print_results_table(results: List[Dict[str, Any]], title: str = "Resultados") -> None:
    """
    Imprime resultados en tabla usando Rich.

    Args:
        results: Lista de resultados
        title: Título de la tabla
    """
    console = Console()
    table = Table(title=title)

    table.add_column("Severidad", style="bold")
    table.add_column("Verificación")
    table.add_column("Ubicación")
    table.add_column("Mensaje")

    for r in results:
        severity = r.get("severity", Severity.INFO)
        if isinstance(severity, str):
            severity = Severity(severity)

        color = SEVERITY_COLORS.get(severity, "white")

        table.add_row(
            f"[{color}]{severity.value.upper()}[/{color}]",
            r.get("check_name", ""),
            r.get("file_path", "") + (f":{r.get('line_number', '')}" if r.get("line_number") else ""),
            r.get("message", "")
        )

    console.print(table)
