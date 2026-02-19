"""
Orquestador de analyzers para DesignReviewer.

Auto-descubre y ejecuta todos los analyzers disponibles en el paquete
`designreviewer.analyzers`. Mismo patrón que CheckOrchestrator de CodeGuard.

Fecha de creación: 2026-02-19
Ticket: 1.4
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Any, List

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

logger = logging.getLogger(__name__)


class AnalyzerOrchestrator:
    """
    Orquesta la ejecución de analyzers de DesignReviewer.

    Responsabilidades:
    1. Auto-discovery de analyzers disponibles (subclases de Verifiable en analyzers/)
    2. Ejecución de todos los analyzers sobre el conjunto de archivos
    3. Manejo de errores: si un analyzer falla, loguea y continúa
    4. Agregación de resultados

    Attributes:
        config: Configuración de DesignReviewer con umbrales por métrica.
        analyzers: Lista de analyzers descubiertos automáticamente.

    Example:
        >>> orchestrator = AnalyzerOrchestrator(config)
        >>> files = [Path("src/service.py"), Path("src/model.py")]
        >>> results = orchestrator.run(files)
        >>> blocking = [r for r in results if r.is_blocking()]
    """

    def __init__(self, config: Any) -> None:
        """
        Inicializa el orquestador.

        Args:
            config: Configuración de DesignReviewer (DesignReviewerConfig una vez
                    implementado el ticket 1.5).
        """
        self.config = config
        self.analyzers: List[Verifiable] = self._discover_analyzers()
        logger.info(
            f"AnalyzerOrchestrator inicializado con {len(self.analyzers)} analyzers descubiertos"
        )

    def _discover_analyzers(self) -> List[Verifiable]:
        """
        Auto-discovery de analyzers en designreviewer.analyzers.

        Importa el módulo `analyzers`, busca todas las clases que heredan de
        `Verifiable` (excluyendo la clase base), las instancia y retorna la lista.

        Returns:
            Lista de instancias de analyzers descubiertos.
        """
        analyzers = []

        try:
            module = importlib.import_module("quality_agents.designreviewer.analyzers")

            for name in dir(module):
                obj = getattr(module, name)

                if (
                    inspect.isclass(obj)
                    and issubclass(obj, Verifiable)
                    and obj is not Verifiable
                ):
                    try:
                        instance = obj()
                        analyzers.append(instance)
                        logger.debug(f"Analyzer descubierto: {instance.name}")
                    except Exception as e:
                        logger.warning(f"Error al instanciar analyzer {name}: {e}. Saltando.")

        except ImportError:
            logger.info(
                "Módulo 'designreviewer.analyzers' no encontrado. "
                "No hay analyzers disponibles todavía."
            )
        except Exception as e:
            logger.error(f"Error durante auto-discovery de analyzers: {e}")

        return analyzers

    def run(self, files: List[Path]) -> List[ReviewResult]:
        """
        Ejecuta todos los analyzers sobre los archivos dados.

        Para cada archivo, crea un ExecutionContext y ejecuta los analyzers
        que decidan correr (según su método should_run). Si un analyzer falla,
        registra el error y continúa con los demás.

        Args:
            files: Lista de archivos Python a analizar.

        Returns:
            Lista agregada de resultados de todos los analyzers.
        """
        if not files:
            return []

        results: List[ReviewResult] = []
        python_files = [f for f in files if f.suffix == ".py"]

        for file_path in python_files:
            context = ExecutionContext(
                file_path=file_path,
                analysis_type="pr-review",
                config=self.config,
            )

            for analyzer in self.analyzers:
                if not analyzer.should_run(context):
                    logger.debug(f"Analyzer {analyzer.name} saltado para {file_path.name}")
                    continue

                try:
                    analyzer_results = analyzer.execute(file_path)
                    results.extend(analyzer_results)
                    logger.debug(
                        f"Analyzer {analyzer.name}: {len(analyzer_results)} resultados "
                        f"en {file_path.name}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error en analyzer {analyzer.name} sobre {file_path}: {e}"
                    )
                    results.append(
                        ReviewResult(
                            analyzer_name=analyzer.name,
                            severity=ReviewSeverity.INFO,
                            current_value=0,
                            threshold=0,
                            message=f"Analyzer falló con error: {e}",
                            file_path=file_path,
                        )
                    )

        logger.info(
            f"Análisis completado: {len(results)} resultados "
            f"en {len(python_files)} archivos"
        )
        return results
