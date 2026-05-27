"""
RelationalCohesionAnalyzer — Cohesión Relacional (H) por paquete.

H (Relational Cohesion) = (R + 1) / N

  R = relaciones internas del paquete (imports entre módulos del mismo paquete)
  N = número de tipos (clases) en el paquete

Rango esperado: 1.5 – 4.0 (según Robert C. Martin)
  H < 1.0 → paquete casi sin cohesión interna
  H ≈ 1.0 → una relación por tipo (mínimo)
  H >> 4.0 → posible over-coupling interno

La granularidad del paquete se controla con `analysis_depth` (default: 1),
igual que DistanceAnalyzer.

Umbral en ArchitectAnalystConfig:
  min_relational_cohesion (default: 1.5) → WARNING si H < umbral

Ticket: Issue #57
Fecha: 2026-05-27
"""

import ast
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

from quality_agents.architectanalyst.metrics.dependency_graph import DependencyGraphBuilder
from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity
from quality_agents.architectanalyst.orchestrator import ProjectMetric


class RelationalCohesionAnalyzer(ProjectMetric):
    """
    Detecta paquetes con baja cohesión relacional (H < min_relational_cohesion).

    Un H bajo indica que las clases del paquete no se usan entre sí —
    probablemente deberían estar en paquetes distintos.

    Severidad: WARNING si H < min_relational_cohesion.
    Paquetes con menos de 2 clases se omiten (H no es significativo).
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "RelationalCohesionAnalyzer"

    @property
    def category(self) -> str:
        return "martin"

    @property
    def estimated_duration(self) -> float:
        return 3.0

    @property
    def priority(self) -> int:
        return 9

    def should_run(self, config: Any) -> bool:
        self._config = config
        if config and hasattr(config, "checks"):
            if not getattr(config.checks, "relational_cohesion", True):
                return False
        return True

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        config = self._config
        threshold = getattr(config, "min_relational_cohesion", 1.5) if config else 1.5
        depth = getattr(config, "analysis_depth", 1) if config else 1

        builder = DependencyGraphBuilder()
        graph = builder.build(project_path, files)

        python_files = [f for f in files if f.suffix == ".py"]
        module_to_file = self._build_module_to_file(project_path, python_files, graph.modules)

        package_data = self._compute_package_metrics(graph, module_to_file, depth)

        results: List[ArchitectureResult] = []

        for pkg in sorted(package_data.keys()):
            n_types = package_data[pkg]["n_types"]
            r_relations = package_data[pkg]["r_relations"]

            # No significativo con menos de 2 clases
            if n_types < 2:
                continue

            h = (r_relations + 1) / n_types

            if h < threshold:
                results.append(ArchitectureResult(
                    analyzer_name=self.name,
                    metric_name="H",
                    module_path=Path(pkg.replace(".", "/")),
                    value=round(h, 3),
                    threshold=threshold,
                    severity=ArchitectureSeverity.WARNING,
                    message=(
                        f"Cohesión Relacional H={h:.2f} < {threshold} en '{pkg}' "
                        f"(R={r_relations} relaciones internas, N={n_types} tipos). "
                        f"Las clases del paquete apenas se relacionan entre sí."
                    ),
                ))

        return results

    def _compute_package_metrics(
        self,
        graph: Any,
        module_to_file: Dict[str, Path],
        depth: int,
    ) -> Dict[str, Dict[str, int]]:
        """
        Calcula N (tipos) y R (relaciones internas) por paquete.

        R cuenta pares (módulo_origen, módulo_destino) dentro del mismo paquete.
        """
        pkg_modules: Dict[str, Set[str]] = defaultdict(set)

        for module in graph.modules:
            pkg = ".".join(module.split(".")[:depth])
            pkg_modules[pkg].add(module)

        result: Dict[str, Dict[str, int]] = {}

        for pkg, modules in pkg_modules.items():
            # N: total de clases en el paquete
            n_types = 0
            for m in modules:
                file_path = module_to_file.get(m)
                if file_path:
                    n_types += self._count_classes(file_path)

            # R: relaciones internas — módulo A del paquete importa módulo B del mismo paquete
            r_relations = 0
            for m in modules:
                for dep in graph.efferent_coupling(m):
                    dep_pkg = ".".join(dep.split(".")[:depth])
                    if dep_pkg == pkg and dep != m:
                        r_relations += 1

            result[pkg] = {"n_types": n_types, "r_relations": r_relations}

        return result

    def _count_classes(self, file_path: Path) -> int:
        """Cuenta el número de clases definidas en el archivo."""
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return 0
        return sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))

    def _build_module_to_file(
        self,
        project_path: Path,
        files: List[Path],
        known_modules: Set[str],
    ) -> Dict[str, Path]:
        """Construye mapa módulo → Path de archivo."""
        builder = DependencyGraphBuilder()
        result: Dict[str, Path] = {}
        for f in files:
            name = builder._path_to_module(f, project_path)
            if name and name in known_modules:
                result[name] = f
        return result
