"""
GodPackageAnalyzer — Detecta paquetes con demasiada concentración.

Un God Package concentra demasiado en una de dos formas:
  1. Demasiadas clases  → responsabilidades mezcladas
  2. Ca muy alto        → casi todo el sistema depende de él

Umbrales en ArchitectAnalystConfig:
  max_package_classes (default: 20) → WARNING si n_clases > umbral
  max_package_ca      (default: 10) → WARNING si Ca > umbral

La granularidad del paquete se controla con `analysis_depth` (default: 1),
igual que DistanceAnalyzer y RelationalCohesionAnalyzer.

Ticket: Issue #58
Fecha: 2026-05-27
"""

import ast
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

from quality_agents.architectanalyst.metrics.dependency_graph import DependencyGraphBuilder
from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity
from quality_agents.architectanalyst.orchestrator import ProjectMetric


class GodPackageAnalyzer(ProjectMetric):
    """
    Detecta paquetes con exceso de clases o acoplamiento aferente (Ca) excesivo.

    WARNING si n_clases > max_package_classes (demasiadas responsabilidades).
    WARNING si Ca > max_package_ca (demasiados dependientes — núcleo frágil).
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "GodPackageAnalyzer"

    @property
    def category(self) -> str:
        return "smells"

    @property
    def estimated_duration(self) -> float:
        return 3.0

    @property
    def priority(self) -> int:
        return 10

    def should_run(self, config: Any) -> bool:
        self._config = config
        if config and hasattr(config, "checks"):
            if not getattr(config.checks, "god_package", True):
                return False
        return True

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        config = self._config
        max_classes = getattr(config, "max_package_classes", 20) if config else 20
        max_ca = getattr(config, "max_package_ca", 10) if config else 10
        depth = getattr(config, "analysis_depth", 1) if config else 1

        builder = DependencyGraphBuilder()
        graph = builder.build(project_path, files)

        python_files = [f for f in files if f.suffix == ".py"]
        module_to_file = self._build_module_to_file(project_path, python_files, graph.modules)

        package_data = self._compute_package_data(graph, module_to_file, depth)

        results: List[ArchitectureResult] = []

        for pkg in sorted(package_data.keys()):
            n_classes = package_data[pkg]["n_classes"]
            ca = package_data[pkg]["ca"]

            if n_classes > max_classes:
                results.append(ArchitectureResult(
                    analyzer_name=self.name,
                    metric_name="GodPackage.Classes",
                    module_path=Path(pkg.replace(".", "/")),
                    value=float(n_classes),
                    threshold=float(max_classes),
                    severity=ArchitectureSeverity.WARNING,
                    message=(
                        f"God Package por tamaño: '{pkg}' tiene {n_classes} clases "
                        f"(umbral: {max_classes}). "
                        f"Demasiadas responsabilidades concentradas en un paquete."
                    ),
                ))

            if ca > max_ca:
                results.append(ArchitectureResult(
                    analyzer_name=self.name,
                    metric_name="GodPackage.Ca",
                    module_path=Path(pkg.replace(".", "/")),
                    value=float(ca),
                    threshold=float(max_ca),
                    severity=ArchitectureSeverity.WARNING,
                    message=(
                        f"God Package por acoplamiento: '{pkg}' tiene Ca={ca} "
                        f"(umbral: {max_ca}). "
                        f"Demasiados paquetes dependen de este paquete."
                    ),
                ))

        return results

    def _compute_package_data(
        self,
        graph: Any,
        module_to_file: Dict[str, Path],
        depth: int,
    ) -> Dict[str, Dict[str, int]]:
        """
        Calcula n_classes (total de clases) y ca (acoplamiento aferente) por paquete.

        Ca cuenta paquetes distintos que tienen al menos un módulo que importa
        algún módulo de este paquete.
        """
        pkg_modules: Dict[str, Set[str]] = defaultdict(set)

        for module in graph.modules:
            pkg = ".".join(module.split(".")[:depth])
            pkg_modules[pkg].add(module)

        all_packages = set(pkg_modules.keys())
        result: Dict[str, Dict[str, int]] = {}

        for pkg, modules in pkg_modules.items():
            # n_classes: total de clases en todos los módulos del paquete
            n_classes = 0
            for m in modules:
                file_path = module_to_file.get(m)
                if file_path:
                    n_classes += self._count_classes(file_path)

            # ca: paquetes distintos que dependen de este paquete
            ca_pkgs: Set[str] = set()
            for other_pkg in all_packages:
                if other_pkg == pkg:
                    continue
                for m in pkg_modules[other_pkg]:
                    for dep in graph.efferent_coupling(m):
                        dep_pkg = ".".join(dep.split(".")[:depth])
                        if dep_pkg == pkg:
                            ca_pkgs.add(other_pkg)
                            break

            result[pkg] = {"n_classes": n_classes, "ca": len(ca_pkgs)}

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
