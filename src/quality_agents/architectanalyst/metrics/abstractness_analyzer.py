"""
AbstractnessAnalyzer — Abstracción (A) por módulo.

A (Abstractness) = clases abstractas / total de clases

Rango: [0.0, 1.0]
  0.0 = sin clases abstractas (todas concretas)
  1.0 = todas las clases son abstractas

Una clase es abstracta si:
  - Hereda de ABC o tiene ABCMeta como metaclase, O
  - Tiene al menos un método decorado con @abstractmethod, O
  - Hereda de Protocol (typing)

A es una métrica informativa sin umbral. Su valor principal es derivar
D (Distance from Main Sequence) junto con I (Instability).
Los resultados son siempre INFO.

Ticket: 2.4
Fecha: 2026-03-01
"""

import ast
from pathlib import Path
from typing import Any, List, Set

from quality_agents.architectanalyst.metrics.dependency_graph import DependencyGraphBuilder
from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity
from quality_agents.architectanalyst.orchestrator import ProjectMetric

# Nombres que marcan una clase como abstracta (via herencia o metaclase)
_ABSTRACT_BASES: Set[str] = {"ABC", "Protocol", "ABCMeta"}


class AbstractnessAnalyzer(ProjectMetric):
    """
    Reporta la abstracción (A) por módulo.

    A = clases abstractas / total de clases

    Emite un resultado INFO por cada módulo que tiene al menos una clase.
    Los módulos sin clases (solo funciones o constantes) se omiten.

    A es una métrica sin umbral — no genera WARNING ni CRITICAL.
    """

    @property
    def name(self) -> str:
        return "AbstractnessAnalyzer"

    @property
    def category(self) -> str:
        return "martin"

    @property
    def estimated_duration(self) -> float:
        return 2.0

    @property
    def priority(self) -> int:
        return 7

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        """
        Analiza el proyecto y reporta A por módulo.

        Args:
            project_path: Directorio raíz del proyecto.
            files: Lista de archivos Python a analizar.

        Returns:
            Lista de ArchitectureResult (INFO) con A para cada módulo con clases.
        """
        builder = DependencyGraphBuilder()
        graph = builder.build(project_path, files)

        # Construir mapa módulo → archivo para poder parsear cada uno
        python_files = [f for f in files if f.suffix == ".py"]
        module_to_file = self._build_module_to_file(project_path, python_files, graph.modules)

        results: List[ArchitectureResult] = []

        for module in sorted(graph.modules):
            file_path = module_to_file.get(module)
            if file_path is None:
                continue

            total, abstracts = self._count_classes(file_path)

            # Módulos sin clases no son relevantes para A
            if total == 0:
                continue

            abstractness = abstracts / total

            results.append(ArchitectureResult(
                analyzer_name=self.name,
                metric_name="A",
                module_path=Path(module.replace(".", "/")),
                value=round(abstractness, 3),
                threshold=None,
                severity=ArchitectureSeverity.INFO,
                message=(
                    f"Abstracción A={abstractness:.2f} "
                    f"({abstracts} abstractas / {total} clases totales)"
                ),
            ))

        return results

    def should_run(self, config: Any) -> bool:
        return True

    # -------------------------------------------------------------------------
    # Métodos auxiliares
    # -------------------------------------------------------------------------

    def _build_module_to_file(
        self,
        project_path: Path,
        files: List[Path],
        known_modules: Set[str],
    ) -> dict:
        """Construye mapa módulo → Path de archivo."""
        from quality_agents.architectanalyst.metrics.dependency_graph import (
            DependencyGraphBuilder as _Builder,
        )

        builder = _Builder()
        result = {}
        for f in files:
            name = builder._path_to_module(f, project_path)
            if name and name in known_modules:
                result[name] = f
        return result

    def _count_classes(self, file_path: Path) -> tuple:
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
        """
        Determina si una clase es abstracta.

        Una clase es abstracta si:
          1. Hereda directamente de ABC, Protocol o ABCMeta, O
          2. Tiene al menos un método decorado con @abstractmethod.
        """
        # Criterio 1: herencia de bases abstractas
        for base in class_node.bases:
            name = self._extract_name(base)
            if name in _ABSTRACT_BASES:
                return True

        # Criterio 2: al menos un @abstractmethod
        for node in ast.walk(class_node):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                dec_name = self._extract_name(decorator)
                if dec_name == "abstractmethod":
                    return True

        return False

    def _extract_name(self, node: ast.expr) -> str:
        """Extrae el nombre de un nodo Name o Attribute."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return ""
