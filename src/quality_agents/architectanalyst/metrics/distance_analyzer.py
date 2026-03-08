"""
DistanceAnalyzer — Distancia a la Main Sequence (D) por paquete.

D (Distance from Main Sequence) = |A + I - 1|

La Main Sequence es la línea ideal A + I = 1. Paquetes sobre esa línea
tienen el balance perfecto entre estabilidad y abstracción.

Las métricas se calculan a nivel de **paquete** (directorio de primer nivel),
no de módulo individual. Esto sigue la definición original de Robert C. Martin
y evita falsos positivos: cualquier clase concreta tiene A=0, I=0 → D=1.00
si se analiza por módulo.

Zonas problemáticas:
  Zone of Pain (A≈0, I≈0): paquete estable pero concreto — muy rígido,
    difícil de cambiar porque muchos dependen de una implementación concreta.
  Zone of Uselessness (A≈1, I≈1): paquete abstracto pero inestable —
    nadie depende de él, las abstracciones no se usan.

Rango de D: [0.0, 1.0]
  0.0 = sobre la Main Sequence (ideal)
  1.0 = máxima distancia

Umbrales en ArchitectAnalystConfig:
  max_distance_warning  (default: 0.3) → WARNING
  max_distance_critical (default: 0.5) → CRITICAL

Ticket: 2.5 / Issue #33
Fecha: 2026-03-01 / 2026-03-08
"""

import ast
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from quality_agents.architectanalyst.metrics._utils import (
    calculate_distance,
    calculate_instability,
)
from quality_agents.architectanalyst.metrics.dependency_graph import DependencyGraphBuilder
from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity
from quality_agents.architectanalyst.orchestrator import ProjectMetric

_ABSTRACT_BASES: Set[str] = {"ABC", "Protocol", "ABCMeta"}


class DistanceAnalyzer(ProjectMetric):
    """
    Detecta módulos alejados de la Main Sequence (D alto).

    D = |A + I - 1|

    Calcula A e I internamente para cada módulo y compara contra los umbrales
    configurados. Solo analiza módulos que tienen al menos una clase definida
    (sin clases, A=0.0 por definición y el resultado sería menos informativo).

    Severidades:
      WARNING  si D > max_distance_warning (default: 0.3)
      CRITICAL si D > max_distance_critical (default: 0.5)
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "DistanceAnalyzer"

    @property
    def category(self) -> str:
        return "martin"

    @property
    def estimated_duration(self) -> float:
        return 4.0

    @property
    def priority(self) -> int:
        return 8

    def should_run(self, config: Any) -> bool:
        self._config = config
        return True

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        """
        Analiza el proyecto y reporta paquetes con D > umbral.

        Las métricas se calculan a nivel de paquete (directorio de primer nivel),
        no de módulo individual, para evitar falsos positivos masivos.

        Args:
            project_path: Directorio raíz del proyecto.
            files: Lista de archivos Python a analizar.

        Returns:
            Lista de ArchitectureResult (WARNING/CRITICAL) para paquetes con D excesivo.
        """
        config = self._config
        warn_threshold = config.max_distance_warning if config is not None else 0.3
        crit_threshold = config.max_distance_critical if config is not None else 0.5

        builder = DependencyGraphBuilder()
        graph = builder.build(project_path, files)

        python_files = [f for f in files if f.suffix == ".py"]
        module_to_file = self._build_module_to_file(project_path, python_files, graph.modules)

        package_data = self._aggregate_to_packages(graph, module_to_file)

        results: List[ArchitectureResult] = []

        for pkg in sorted(package_data.keys()):
            data = package_data[pkg]
            total_classes = data["total_classes"]

            # Paquetes sin clases no tienen A significativo
            if total_classes == 0:
                continue

            abstractness = data["abstract_classes"] / total_classes
            ca = data["ca"]
            ce = data["ce"]
            instability = calculate_instability(ca, ce)
            distance = calculate_distance(instability, abstractness)

            if distance <= warn_threshold:
                continue

            severity = (
                ArchitectureSeverity.CRITICAL
                if distance > crit_threshold
                else ArchitectureSeverity.WARNING
            )

            zone = self._identify_zone(instability, abstractness)

            results.append(ArchitectureResult(
                analyzer_name=self.name,
                metric_name="D",
                module_path=Path(pkg),
                value=round(distance, 3),
                threshold=warn_threshold,
                severity=severity,
                message=(
                    f"Distancia D={distance:.2f} > {warn_threshold} "
                    f"(A={abstractness:.2f}, I={instability:.2f}, "
                    f"Ca={ca}, Ce={ce}). {zone}"
                ),
            ))

        return results

    # -------------------------------------------------------------------------
    # Métodos auxiliares
    # -------------------------------------------------------------------------

    def _aggregate_to_packages(
        self,
        graph: Any,
        module_to_file: Dict[str, Path],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Agrega métricas de módulos individuales al nivel de paquete.

        Un paquete es el primer componente del nombre dotted del módulo.
        Por ejemplo: `entidades.sensor` → paquete `entidades`.

        Ca y Ce se calculan contando dependencias **entre paquetes distintos**,
        no entre módulos individuales.

        Args:
            graph: DependencyGraph con módulos y sus dependencias.
            module_to_file: Mapa módulo → archivo para parsear clases.

        Returns:
            Diccionario paquete → {abstract_classes, total_classes, ca, ce}.
        """
        pkg_classes: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"abstract_classes": 0, "total_classes": 0}
        )
        pkg_modules: Dict[str, Set[str]] = defaultdict(set)

        for module in graph.modules:
            pkg = module.split(".")[0]
            pkg_modules[pkg].add(module)

            file_path = module_to_file.get(module)
            if file_path:
                total, abstracts = self._count_classes(file_path)
                pkg_classes[pkg]["total_classes"] += total
                pkg_classes[pkg]["abstract_classes"] += abstracts

        all_packages = set(pkg_modules.keys())
        result: Dict[str, Dict[str, Any]] = {}

        for pkg in all_packages:
            # Ce: paquetes distintos de los que depende este paquete
            ce_pkgs: Set[str] = set()
            for m in pkg_modules[pkg]:
                for dep in graph.efferent_coupling(m):
                    dep_pkg = dep.split(".")[0]
                    if dep_pkg != pkg and dep_pkg in all_packages:
                        ce_pkgs.add(dep_pkg)

            # Ca: paquetes distintos que dependen de este paquete
            ca_pkgs: Set[str] = set()
            for other_pkg in all_packages:
                if other_pkg == pkg:
                    continue
                for m in pkg_modules[other_pkg]:
                    for dep in graph.efferent_coupling(m):
                        if dep.split(".")[0] == pkg:
                            ca_pkgs.add(other_pkg)
                            break

            result[pkg] = {
                "abstract_classes": pkg_classes[pkg]["abstract_classes"],
                "total_classes": pkg_classes[pkg]["total_classes"],
                "ca": len(ca_pkgs),
                "ce": len(ce_pkgs),
            }

        return result

    def _identify_zone(self, instability: float, abstractness: float) -> str:
        """Identifica la zona problemática (Pain o Uselessness)."""
        if instability < 0.3 and abstractness < 0.3:
            return "Zone of Pain: módulo estable pero concreto (muy rígido)."
        if instability > 0.7 and abstractness > 0.7:
            return "Zone of Uselessness: módulo abstracto pero nadie depende de él."
        return "Alejado de la Main Sequence."

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

    def _count_classes(self, file_path: Path) -> Tuple[int, int]:
        """
        Cuenta clases totales y abstractas en un archivo.

        Returns:
            (total_classes, abstract_classes)
        """
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return 0, 0

        total = 0
        abstracts = 0

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            total += 1
            if self._is_abstract(node):
                abstracts += 1

        return total, abstracts

    def _is_abstract(self, class_node: ast.ClassDef) -> bool:
        """Determina si una clase es abstracta."""
        for base in class_node.bases:
            if self._extract_name(base) in _ABSTRACT_BASES:
                return True

        # metaclass=ABCMeta vive en keywords, no en bases
        for kw in class_node.keywords:
            if kw.arg == "metaclass" and self._extract_name(kw.value) == "ABCMeta":
                return True

        for node in ast.walk(class_node):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if self._extract_name(decorator) == "abstractmethod":
                    return True

        return False

    def _extract_name(self, node: ast.expr) -> Optional[str]:
        """Extrae el nombre de un nodo Name o Attribute."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return None
