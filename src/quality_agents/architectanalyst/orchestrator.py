"""
Orquestador de métricas para ArchitectAnalyst.

Auto-descubre y ejecuta todas las métricas disponibles en el paquete
`architectanalyst.metrics`. Mismo patrón de discovery que AnalyzerOrchestrator
de DesignReviewer, pero con ejecución project-wide en lugar de archivo por archivo.

A diferencia de CodeGuard y DesignReviewer, las métricas de ArchitectAnalyst
analizan el proyecto completo de una vez (Ca/Ce requieren ver todos los imports
del proyecto para calcular acoplamiento aferente y eferente).

Fecha de creación: 2026-02-28
Ticket: 1.3
"""

import importlib
import inspect
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Optional

from quality_agents.architectanalyst.models import ArchitectureResult

logger = logging.getLogger(__name__)


class ProjectMetric(ABC):
    """
    Clase base abstracta para métricas de arquitectura de ArchitectAnalyst.

    A diferencia de Verifiable (que trabaja archivo por archivo), ProjectMetric
    recibe el proyecto completo de una vez. Esto es necesario porque las métricas
    de arquitectura son inherentemente cross-module:
        - Ca (Afferent Coupling): cuántos módulos dependen de este → necesita todos los archivos
        - Ce (Efferent Coupling): cuántos módulos importa este → necesita los imports de cada uno
        - DependencyCycles: DFS sobre el grafo completo de imports
        - LayerViolations: verifica imports contra reglas de capas declaradas en config

    Subclases deben implementar:
        - name: Nombre identificador único
        - category: Categoría ("martin", "structural", "cycles")
        - analyze: Lógica de análisis sobre el proyecto completo

    Subclases pueden sobrescribir:
        - estimated_duration: Duración estimada (default: 5.0s)
        - priority: Prioridad de ejecución (default: 5)
        - should_run: Lógica de activación según config (default: True)

    Example:
        >>> class CouplingAnalyzer(ProjectMetric):
        ...     @property
        ...     def name(self) -> str:
        ...         return "CouplingAnalyzer"
        ...
        ...     @property
        ...     def category(self) -> str:
        ...         return "martin"
        ...
        ...     def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        ...         # Construir grafo de imports y calcular Ca/Ce por módulo
        ...         ...
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre identificador único de la métrica."""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """
        Categoría de la métrica.

        Una de: "martin", "structural", "cycles"
        """
        pass

    @property
    def estimated_duration(self) -> float:
        """
        Duración estimada en segundos.

        Las métricas de arquitectura son más lentas que los checks de CodeGuard
        porque requieren análisis cross-module. Default: 5.0s.
        """
        return 5.0

    @property
    def priority(self) -> int:
        """
        Prioridad de ejecución (1 = más alta, 10 = más baja).

        Guía:
            1-2: Ciclos de dependencias (bloquean la comprensión del sistema)
            3-4: Violaciones de capas (arquitectura declarada)
            5-6: Métricas de Martin (Ca, Ce, I, A, D)
        """
        return 5

    def should_run(self, config: Any) -> bool:
        """
        Determina si esta métrica debe ejecutarse según la configuración.

        La implementación default siempre retorna True.
        Subclases pueden sobrescribir para desactivarse via config.

        Args:
            config: Configuración de ArchitectAnalyst (ArchitectAnalystConfig).

        Returns:
            True si debe ejecutarse.
        """
        return True

    @abstractmethod
    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        """
        Ejecuta el análisis sobre el proyecto completo.

        Args:
            project_path: Directorio raíz del proyecto.
            files: Lista de archivos Python a analizar.

        Returns:
            Lista de ArchitectureResult (uno por módulo o violación detectada).

        Raises:
            Puede lanzar excepciones. El orquestador las captura y continúa.
        """
        pass


class MetricOrchestrator:
    """
    Orquesta la ejecución de métricas de ArchitectAnalyst.

    Responsabilidades:
    1. Auto-discovery de métricas disponibles (subclases de ProjectMetric en metrics/)
    2. Ejecución project-wide: pasa todos los archivos a cada métrica de una vez
    3. Manejo de errores: si una métrica falla, loguea y continúa
    4. Agregación de resultados

    Attributes:
        config: Configuración de ArchitectAnalyst con umbrales por métrica.
        metrics: Lista de métricas descubiertas automáticamente.

    Example:
        >>> orchestrator = MetricOrchestrator(config)
        >>> files = list(Path("src").rglob("*.py"))
        >>> results = orchestrator.run(files)
        >>> criticals = [r for r in results if r.is_critical()]
    """

    def __init__(self, config: Any) -> None:
        """
        Inicializa el orquestador.

        Args:
            config: Configuración de ArchitectAnalyst (ArchitectAnalystConfig).
        """
        self.config = config
        self.metrics: List[ProjectMetric] = self._discover_metrics()
        logger.info(
            f"MetricOrchestrator inicializado con {len(self.metrics)} métricas descubiertas"
        )

    def _discover_metrics(self) -> List[ProjectMetric]:
        """
        Auto-discovery de métricas en architectanalyst.metrics.

        Importa el módulo `metrics`, busca todas las clases que heredan de
        `ProjectMetric` (excluyendo la clase base), las instancia y retorna la lista
        ordenada por prioridad.

        Returns:
            Lista de instancias de métricas descubiertas, ordenadas por priority.
        """
        discovered: List[ProjectMetric] = []

        try:
            module = importlib.import_module("quality_agents.architectanalyst.metrics")

            for name in dir(module):
                obj = getattr(module, name)

                if (
                    inspect.isclass(obj)
                    and issubclass(obj, ProjectMetric)
                    and obj is not ProjectMetric
                ):
                    try:
                        instance = obj()
                        discovered.append(instance)
                        logger.debug(f"Métrica descubierta: {instance.name}")
                    except Exception as e:
                        logger.warning(f"Error al instanciar métrica {name}: {e}. Saltando.")

        except ImportError:
            logger.info(
                "Módulo 'architectanalyst.metrics' no encontrado. "
                "No hay métricas disponibles todavía."
            )
        except Exception as e:
            logger.error(f"Error durante auto-discovery de métricas: {e}")

        return sorted(discovered, key=lambda m: m.priority)

    def run(self, files: List[Path]) -> List[ArchitectureResult]:
        """
        Ejecuta todas las métricas sobre el proyecto.

        A diferencia de AnalyzerOrchestrator, pasa todos los archivos a cada
        métrica de una vez (no archivo por archivo) porque las métricas de
        arquitectura requieren visión cross-module.

        Args:
            files: Lista de archivos Python a analizar.

        Returns:
            Lista agregada de resultados de todas las métricas.
        """
        if not files:
            return []

        python_files = [f for f in files if f.suffix == ".py"]
        if not python_files:
            return []

        project_path = self._find_project_root(python_files[0])
        results: List[ArchitectureResult] = []

        for metric in self.metrics:
            if not metric.should_run(self.config):
                logger.debug(f"Métrica {metric.name} desactivada por config")
                continue

            try:
                metric_results = metric.analyze(project_path, python_files)
                results.extend(metric_results)
                logger.debug(f"Métrica {metric.name}: {len(metric_results)} resultados")
            except Exception as e:
                logger.error(f"Error en métrica {metric.name}: {e}")

        logger.info(
            f"Análisis completado: {len(results)} resultados "
            f"de {len(self.metrics)} métricas sobre {len(python_files)} archivos"
        )
        return results

    def _find_project_root(self, file_path: Path) -> Path:
        """
        Encuentra la raíz del proyecto subiendo por el árbol de directorios.

        Busca `pyproject.toml`, `setup.py` o `setup.cfg` como indicadores.

        Args:
            file_path: Cualquier archivo del proyecto.

        Returns:
            Directorio raíz del proyecto.
        """
        indicators = {"pyproject.toml", "setup.py", "setup.cfg"}
        current = file_path.parent if file_path.is_file() else file_path

        while current != current.parent:
            if any((current / ind).exists() for ind in indicators):
                return current
            current = current.parent

        return file_path.parent

    def _find_project_root_from_files(self, files: List[Path]) -> Optional[Path]:
        """
        Variante que acepta lista de archivos. Retorna None si la lista está vacía.
        """
        if not files:
            return None
        return self._find_project_root(files[0])
