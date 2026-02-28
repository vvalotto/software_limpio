"""
Funciones matemáticas puras de las Métricas de Martin.

Usadas internamente por los analyzers de Fase 2 (CouplingAnalyzer,
InstabilityAnalyzer, AbstractnessAnalyzer, DistanceAnalyzer).

Ticket: 1.5
"""


def calculate_instability(ca: int, ce: int) -> float:
    """
    Calcula I (Instability) = Ce / (Ca + Ce).

    Args:
        ca: Afferent Coupling — módulos externos que dependen de este.
        ce: Efferent Coupling — módulos de los que depende este.

    Returns:
        Instabilidad en [0.0, 1.0].
        0.0 = totalmente estable (nada depende de él).
        1.0 = totalmente inestable (no depende nadie de él).
        0.0 si ca = ce = 0 (módulo aislado).
    """
    total = ca + ce
    if total == 0:
        return 0.0
    return ce / total


def calculate_distance(instability: float, abstractness: float) -> float:
    """
    Calcula D (Distance from Main Sequence) = |A + I - 1|.

    La Main Sequence es la línea ideal donde A + I = 1.
    Módulos sobre esa línea tienen el balance perfecto entre estabilidad y abstracción.

    Args:
        instability: Valor de I en [0.0, 1.0].
        abstractness: Valor de A en [0.0, 1.0].

    Returns:
        Distancia en [0.0, 1.0].
        0.0 = sobre la Main Sequence (ideal).
        1.0 = máxima distancia (Zone of Pain o Zone of Uselessness).
    """
    return abs(abstractness + instability - 1)
