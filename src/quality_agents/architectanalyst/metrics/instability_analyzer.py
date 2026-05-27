"""
InstabilityAnalyzer — Inestabilidad (I) por módulo.

I (Instability) = Ce / (Ca + Ce)

Rango: [0.0, 1.0]
  0.0 = totalmente estable — muchos dependen de él, él no depende de nadie
  1.0 = totalmente inestable — nadie depende de él, él depende de muchos

Con layer_roles, los módulos pueden tener roles explícitos que ajustan la lógica:
  stable: se advierte si I > max_instability (comportamiento default)
  leaf:   módulo terminal — se advierte si I < (1 - max_instability),
          porque algo depende de él cuando no debería.

Ticket: 2.3 / Issue #47
Fecha: 2026-03-01 / 2026-05-27
"""

import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional

from quality_agents.architectanalyst.metrics._utils import calculate_instability
from quality_agents.architectanalyst.metrics.dependency_graph import DependencyGraphBuilder
from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity
from quality_agents.architectanalyst.orchestrator import ProjectMetric

_VALID_ROLES = {"leaf", "stable"}


class InstabilityAnalyzer(ProjectMetric):
    """
    Detecta módulos con inestabilidad excesiva o inadecuada según su rol arquitectural.

    Comportamiento por defecto (sin layer_roles):
        WARNING si I > max_instability

    Con layer_roles configurado:
        stable → WARNING si I > max_instability (igual que default)
        leaf   → WARNING si I < (1 - max_instability): algo depende de un módulo terminal

    Umbral por defecto: 0.8 (configurable vía max_instability en pyproject.toml).
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "InstabilityAnalyzer"

    @property
    def category(self) -> str:
        return "martin"

    @property
    def estimated_duration(self) -> float:
        return 3.0

    @property
    def priority(self) -> int:
        return 6

    def should_run(self, config: Any) -> bool:
        self._config = config
        if config and hasattr(config, "checks") and not config.checks.instability:
            return False
        return True

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        config = self._config
        threshold = config.max_instability if config is not None else 0.8
        layer_roles: Dict[str, str] = getattr(config, "layer_roles", {}) if config else {}

        builder = DependencyGraphBuilder()
        graph = builder.build(project_path, files)

        results: List[ArchitectureResult] = []

        for module in sorted(graph.modules):
            ca = len(graph.afferent_coupling(module))
            ce = len(graph.efferent_coupling(module))

            if ca == 0 and ce == 0:
                continue

            instability = calculate_instability(ca, ce)
            role = self._resolve_role(module, layer_roles)

            result = self._evaluar_modulo(module, instability, ca, ce, threshold, role)
            if result:
                results.append(result)

        return results

    def _resolve_role(self, module: str, layer_roles: Dict[str, str]) -> Optional[str]:
        """
        Retorna el rol del módulo según layer_roles, o None si no hay match.

        El módulo se convierte a formato de path (puntos → barras) para
        que los patrones glob funcionen naturalmente (*/application/commands/*).
        """
        module_path = module.replace(".", "/")
        for pattern, role in layer_roles.items():
            if role in _VALID_ROLES and fnmatch.fnmatch(module_path, pattern):
                return role
        return None

    def _evaluar_modulo(
        self,
        module: str,
        instability: float,
        ca: int,
        ce: int,
        threshold: float,
        role: Optional[str],
    ) -> Optional[ArchitectureResult]:
        """Evalúa un módulo y retorna un resultado si hay violación, o None."""
        module_path = Path(module.replace(".", "/"))

        if role == "leaf":
            # Un leaf debería ser inestable (nadie depende de él).
            # Si I es bajo significa que algo depende de él — inesperado.
            leaf_threshold = 1.0 - threshold
            if instability < leaf_threshold:
                return ArchitectureResult(
                    analyzer_name=self.name,
                    metric_name="I",
                    module_path=module_path,
                    value=round(instability, 3),
                    threshold=leaf_threshold,
                    severity=ArchitectureSeverity.WARNING,
                    message=(
                        f"Leaf module '{module}' tiene I={instability:.2f} < {leaf_threshold:.2f}. "
                        f"Un módulo terminal no debería tener dependientes (Ca={ca}). "
                        f"Verificar si la arquitectura CQRS/ES está bien estructurada."
                    ),
                )
            return None

        # Rol "stable" o sin rol: comportamiento por defecto
        if instability > threshold:
            role_info = f" [rol: {role}]" if role else ""
            return ArchitectureResult(
                analyzer_name=self.name,
                metric_name="I",
                module_path=module_path,
                value=round(instability, 3),
                threshold=threshold,
                severity=ArchitectureSeverity.WARNING,
                message=(
                    f"Inestabilidad I={instability:.2f} > {threshold}{role_info} "
                    f"(Ca={ca}, Ce={ce}). Módulo depende de muchos otros "
                    f"sin que nadie estabilice sus dependencias."
                ),
            )
        return None
