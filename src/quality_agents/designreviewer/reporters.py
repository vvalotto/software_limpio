"""
Generadores de reportes para DesignReviewer.
"""

from pathlib import Path
from typing import List

from .models import ReviewResult


def generate_html_report(results: List[ReviewResult], output_path: Path) -> None:
    """
    Genera reporte HTML con los resultados del análisis.

    Args:
        results: Lista de resultados de análisis
        output_path: Ruta donde guardar el reporte
    """
    # TODO: Implementar con Jinja2
    pass


def generate_json_report(results: List[ReviewResult], output_path: Path) -> None:
    """
    Genera reporte JSON con los resultados del análisis.

    Args:
        results: Lista de resultados de análisis
        output_path: Ruta donde guardar el reporte
    """
    # TODO: Implementar
    pass


def generate_summary(results: List[ReviewResult]) -> str:
    """
    Genera resumen textual de los resultados.

    Args:
        results: Lista de resultados de análisis

    Returns:
        Resumen en texto plano
    """
    # TODO: Implementar
    return ""
