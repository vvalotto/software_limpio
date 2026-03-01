"""
LayerViolationsAnalyzer — Violaciones de arquitectura en capas.

Detecta imports que violan las reglas de dependencia entre capas declaradas
en la sección [tool.architectanalyst.layers] de pyproject.toml.

Ejemplo de configuración:
    [tool.architectanalyst.layers]
    domain = []
    application = ["domain"]
    infrastructure = ["application", "domain"]

Con estas reglas, un import de `domain` hacia `application` sería CRITICAL
porque la capa "domain" no puede depender de "application".

Se desactiva automáticamente si no hay reglas configuradas (LayersConfig vacío).
Cualquier violación detectada es siempre CRITICAL (threshold=0, no configurable).

Ticket: 3.2
Fecha: 2026-03-01
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from quality_agents.architectanalyst.metrics.dependency_graph import DependencyGraphBuilder
from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity
from quality_agents.architectanalyst.orchestrator import ProjectMetric

logger = logging.getLogger(__name__)


class LayerViolationsAnalyzer(ProjectMetric):
    """
    Detecta imports que violan las reglas de dependencia entre capas.

    El nombre de la capa debe aparecer como segmento del nombre de módulo dotted.
    Ejemplo: dado layer="domain", el módulo "mipkg.domain.repository" pertenece
    a la capa "domain" porque "domain" es uno de sus segmentos.

    Cuando varios segmentos coinciden con nombres de capas, se toma el primero
    (más cercano a la raíz del paquete), que corresponde al nivel de capa habitual
    en arquitecturas DDD/Clean Architecture.

    Severidad: siempre CRITICAL. threshold=0 (no configurable).
    Se desactiva si LayersConfig.is_configured() → False.
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "LayerViolationsAnalyzer"

    @property
    def category(self) -> str:
        return "cycles"

    @property
    def estimated_duration(self) -> float:
        return 3.0

    @property
    def priority(self) -> int:
        return 2

    def should_run(self, config: Any) -> bool:
        """
        Solo se ejecuta si hay reglas de capas configuradas.

        Args:
            config: ArchitectAnalystConfig.

        Returns:
            True solo si config.layers.is_configured() → True.
        """
        self._config = config
        if config is None:
            return False
        return config.layers.is_configured()

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        """
        Analiza el proyecto y reporta cada violación de capas detectada.

        Args:
            project_path: Directorio raíz del proyecto.
            files: Lista de archivos Python a analizar.

        Returns:
            Lista de ArchitectureResult CRITICAL, uno por violación detectada.
        """
        config = self._config
        rules: Dict[str, List[str]] = config.layers.rules

        builder = DependencyGraphBuilder()
        graph = builder.build(project_path, files)

        results: List[ArchitectureResult] = []

        for module in sorted(graph.modules):
            module_layer = self._find_layer(module, rules)
            if module_layer is None:
                continue

            allowed_layers = rules[module_layer]

            for dep in sorted(graph.efferent_coupling(module)):
                dep_layer = self._find_layer(dep, rules)
                if dep_layer is None:
                    continue

                # Dependencias dentro de la misma capa son siempre permitidas
                if dep_layer == module_layer:
                    continue

                if dep_layer not in allowed_layers:
                    allowed_str = ", ".join(f"'{a}'" for a in allowed_layers) if allowed_layers else "ninguna"
                    results.append(ArchitectureResult(
                        analyzer_name=self.name,
                        metric_name="LayerViolation",
                        module_path=Path(module.replace(".", "/")),
                        value=1.0,
                        threshold=0.0,
                        severity=ArchitectureSeverity.CRITICAL,
                        message=(
                            f"Violación de capas: '{module}' (capa '{module_layer}') "
                            f"importa de '{dep}' (capa '{dep_layer}'). "
                            f"'{module_layer}' solo puede depender de: {allowed_str}."
                        ),
                    ))

        return results

    # -------------------------------------------------------------------------
    # Método auxiliar
    # -------------------------------------------------------------------------

    def _find_layer(self, module: str, rules: Dict[str, List[str]]) -> Optional[str]:
        """
        Encuentra la capa a la que pertenece un módulo.

        Compara cada segmento del nombre de módulo dotted contra los nombres
        de capas declarados. Retorna el primer segmento que coincida.

        Args:
            module: Nombre de módulo dotted (ej: "mipkg.domain.repository").
            rules: Reglas de capas (nombre de capa → capas permitidas).

        Returns:
            Nombre de la capa si se encuentra, None si el módulo no pertenece
            a ninguna capa declarada.
        """
        parts = module.split(".")
        for part in parts:
            if part in rules:
                return part
        return None
