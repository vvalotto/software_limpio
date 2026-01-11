"""
Cálculo de métricas de arquitectura.
"""

from pathlib import Path
from typing import Dict, List, Tuple


def calculate_afferent_coupling(module_path: Path) -> int:
    """
    Calcula Ca (Afferent Coupling) - módulos que dependen de este.

    Args:
        module_path: Ruta al módulo

    Returns:
        Número de módulos que dependen de este
    """
    # TODO: Implementar
    return 0


def calculate_efferent_coupling(module_path: Path) -> int:
    """
    Calcula Ce (Efferent Coupling) - módulos de los que este depende.

    Args:
        module_path: Ruta al módulo

    Returns:
        Número de módulos de los que depende
    """
    # TODO: Implementar
    return 0


def calculate_instability(ca: int, ce: int) -> float:
    """
    Calcula I (Instability) = Ce / (Ca + Ce).

    Args:
        ca: Afferent Coupling
        ce: Efferent Coupling

    Returns:
        Instabilidad (0 = estable, 1 = inestable)
    """
    total = ca + ce
    if total == 0:
        return 0.0
    return ce / total


def calculate_abstractness(module_path: Path) -> float:
    """
    Calcula A (Abstractness) = abstracciones / total clases.

    Args:
        module_path: Ruta al módulo

    Returns:
        Abstractness (0 = concreto, 1 = abstracto)
    """
    # TODO: Implementar
    return 0.0


def calculate_distance_from_main_sequence(instability: float, abstractness: float) -> float:
    """
    Calcula D (Distance) = |A + I - 1|.

    Ideal: D ≈ 0 (sobre la línea principal)

    Args:
        instability: Valor de I
        abstractness: Valor de A

    Returns:
        Distancia de la secuencia principal
    """
    return abs(abstractness + instability - 1)


def analyze_package_metrics(package_path: Path) -> Dict[str, Dict[str, float]]:
    """
    Analiza métricas de Martin para todos los módulos de un paquete.

    Args:
        package_path: Ruta al paquete

    Returns:
        Diccionario con métricas por módulo
    """
    # TODO: Implementar
    return {}
