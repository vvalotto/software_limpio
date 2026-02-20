"""
Tipos de datos de DesignReviewer.

Define ReviewSeverity, SolidPrinciple y ReviewResult, los tipos propios del agente.
Independientes de los tipos de CodeGuard — solo comparten Verifiable de shared/.

Ticket: 1.2 (extendido en Ticket 4.1)
Fecha: 2026-02-19
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ReviewSeverity(Enum):
    """Niveles de severidad para los resultados de análisis de diseño."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class SolidPrinciple(Enum):
    """Principios SOLID que pueden ser violados por code smells."""

    SRP = "S"  # Single Responsibility Principle
    OCP = "O"  # Open/Closed Principle
    LSP = "L"  # Liskov Substitution Principle
    ISP = "I"  # Interface Segregation Principle
    DIP = "D"  # Dependency Inversion Principle


@dataclass
class ReviewResult:
    """
    Resultado de un analyzer individual de DesignReviewer.

    Attributes:
        analyzer_name: Nombre del analyzer que generó el resultado.
        severity: Nivel de severidad (INFO, WARNING, CRITICAL).
        current_value: Valor medido por el analyzer.
        threshold: Umbral configurado para esta métrica.
        message: Descripción del problema detectado.
        file_path: Archivo donde se detectó el problema.
        class_name: Clase afectada (None si aplica al módulo completo).
        suggestion: Sugerencia de refactoring (puede ser enriquecida por IA).
        estimated_effort: Estimación de horas de refactoring necesarias.
        solid_principle: Principio SOLID violado (solo para smells de Fase 4).
        smell_type: Tipo de code smell detectado (solo para smells de Fase 4).
    """

    analyzer_name: str
    severity: ReviewSeverity
    current_value: float | int
    threshold: float | int
    message: str
    file_path: Path
    class_name: str | None = None
    suggestion: str | None = None
    estimated_effort: float = field(default=0.0)
    solid_principle: SolidPrinciple | None = None  # Principio SOLID violado (Fase 4)
    smell_type: str | None = None  # Tipo de code smell (ej: "GodObject", "LongMethod")

    def is_blocking(self) -> bool:
        """Retorna True si este resultado debe bloquear el merge."""
        return self.severity == ReviewSeverity.CRITICAL

    def __str__(self) -> str:
        location = f"{self.file_path}"
        if self.class_name:
            location += f"::{self.class_name}"
        return (
            f"[{self.severity.value.upper()}] {self.analyzer_name} — {self.message} "
            f"(valor: {self.current_value}, umbral: {self.threshold}) @ {location}"
        )
