"""
Módulo de abstracción para verificaciones modulares.

Define la clase base `Verifiable` y el contexto de ejecución `ExecutionContext`
para el sistema de verificación modular con orquestación contextual.

Fecha de creación: 2026-02-03
Basado en: docs/agentes/decision_arquitectura_checks_modulares.md
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional


@dataclass
class ExecutionContext:
    """
    Contexto de ejecución para decisiones inteligentes de verificación.

    Este contexto permite a los verificables (checks/analyzers/metrics) decidir
    si deben ejecutarse basándose en información del archivo, tipo de análisis,
    presupuesto de tiempo y configuración.

    Attributes:
        file_path: Ruta al archivo a verificar/analizar
        is_new_file: True si el archivo es nuevo (no existe en git/vcs)
        is_modified: True si el archivo fue modificado
        analysis_type: Tipo de análisis ("pre-commit", "pr-review", "full", "sprint-end")
        time_budget: Segundos disponibles para completar el análisis (None = sin límite)
        config: Configuración del agente (CodeGuardConfig, etc.)
        is_excluded: True si el archivo está en patrones de exclusión
        ai_enabled: True si IA está habilitada para explicaciones/sugerencias
        ai_suggestions: Sugerencias previas de IA (opcional)
    """

    file_path: Path
    is_new_file: bool = False
    is_modified: bool = True
    analysis_type: str = "full"
    time_budget: Optional[float] = None
    config: Any = None
    is_excluded: bool = False
    ai_enabled: bool = False
    ai_suggestions: Optional[List[str]] = field(default_factory=lambda: None)


class Verifiable(ABC):
    """
    Clase base abstracta para todos los verificables (checks, analyzers, metrics).

    Esta clase implementa el patrón Strategy con decisión contextual, permitiendo
    que cada verificable decida autónomamente si debe ejecutarse según el contexto.

    Los verificables son componentes cohesivos y modulares que:
    - Se auto-descubren automáticamente (via orchestrator)
    - Deciden cuándo ejecutarse (método should_run)
    - Ejecutan su lógica específica (método execute)
    - Tienen metadata de prioridad y duración estimada

    Subclases deben implementar:
        - name: Nombre identificador único
        - category: Categoría del verificable
        - execute: Lógica de verificación/análisis

    Subclases pueden sobrescribir:
        - estimated_duration: Duración estimada (default: 1.0s)
        - priority: Prioridad de ejecución (default: 5)
        - should_run: Lógica de decisión contextual (default: not context.is_excluded)

    Example:
        >>> class PEP8Check(Verifiable):
        ...     @property
        ...     def name(self) -> str:
        ...         return "PEP8"
        ...
        ...     @property
        ...     def category(self) -> str:
        ...         return "style"
        ...
        ...     def should_run(self, context: ExecutionContext) -> bool:
        ...         return context.file_path.suffix == ".py" and not context.is_excluded
        ...
        ...     def execute(self, file_path: Path) -> List[CheckResult]:
        ...         # Ejecutar flake8 y retornar resultados
        ...         return results
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Nombre identificador único del verificable.

        Returns:
            Nombre corto (ej: "PEP8", "Pylint", "CyclomaticComplexity")
        """
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """
        Categoría del verificable.

        Returns:
            Una de: "style", "quality", "security", "design", "architecture"
        """
        pass

    @property
    def estimated_duration(self) -> float:
        """
        Duración estimada de ejecución en segundos.

        Usado por el orquestador para decisiones de presupuesto de tiempo.
        Checks rápidos (< 1s) tienen prioridad en análisis pre-commit.

        Returns:
            Segundos estimados (default: 1.0)
        """
        return 1.0

    @property
    def priority(self) -> int:
        """
        Prioridad de ejecución del verificable.

        Escala: 1 (más alta) a 10 (más baja).
        Usado cuando hay restricción de tiempo para priorizar checks críticos.

        Guía de prioridades:
            1-2: Crítico (seguridad, sintaxis)
            3-4: Alta (estilo, complejidad)
            5-6: Media (métricas de diseño)
            7-8: Baja (optimizaciones, sugerencias)
            9-10: Muy baja (experimental)

        Returns:
            Número de prioridad (default: 5 = media)
        """
        return 5

    def should_run(self, context: ExecutionContext) -> bool:
        """
        Determina si este verificable debe ejecutarse en el contexto dado.

        Esta es la clave del sistema modular: cada verificable decide autónomamente
        si debe ejecutarse basándose en el contexto (tipo de archivo, análisis,
        configuración, tiempo disponible, etc.).

        La implementación default solo verifica que el archivo no esté excluido.
        Subclases deben sobrescribir para agregar lógica específica.

        Args:
            context: Contexto de ejecución con información del archivo/análisis

        Returns:
            True si debe ejecutarse, False si debe saltarse

        Example:
            >>> def should_run(self, context: ExecutionContext) -> bool:
            ...     # Solo archivos Python no excluidos
            ...     if context.is_excluded or context.file_path.suffix != ".py":
            ...         return False
            ...
            ...     # Solo si el check está habilitado en config
            ...     if context.config and not context.config.check_pep8:
            ...         return False
            ...
            ...     # En pre-commit siempre (es rápido)
            ...     if context.analysis_type == "pre-commit":
            ...         return True
            ...
            ...     # En otros contextos, verificar presupuesto
            ...     if context.time_budget is not None:
            ...         return context.time_budget >= self.estimated_duration
            ...
            ...     return True
        """
        return not context.is_excluded

    @abstractmethod
    def execute(self, file_path: Path) -> List[Any]:
        """
        Ejecuta la verificación/análisis sobre el archivo.

        Este método contiene la lógica específica del verificable.
        Debe ser implementado por cada subclase.

        Args:
            file_path: Ruta al archivo a verificar/analizar

        Returns:
            Lista de resultados:
                - CheckResult para CodeGuard
                - AnalysisResult para DesignReviewer
                - MetricResult para ArchitectAnalyst

        Raises:
            Puede lanzar excepciones específicas del tool (TimeoutError, FileNotFoundError, etc.)
            El orquestador es responsable de manejar excepciones.

        Example:
            >>> def execute(self, file_path: Path) -> List[CheckResult]:
            ...     results = []
            ...     # Ejecutar tool externo
            ...     process = subprocess.run(["flake8", str(file_path)], ...)
            ...     # Parsear resultados
            ...     for line in process.stdout.split("\\n"):
            ...         results.append(CheckResult(...))
            ...     return results
        """
        pass
