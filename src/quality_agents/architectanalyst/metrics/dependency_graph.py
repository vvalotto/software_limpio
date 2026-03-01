"""
DependencyGraphBuilder — Grafo dirigido de dependencias entre módulos.

Helper interno usado por CouplingAnalyzer, InstabilityAnalyzer,
AbstractnessAnalyzer y DistanceAnalyzer para construir el grafo de imports
del proyecto de forma consistente.

Solo se procesan imports absolutos. Los imports relativos (level > 0) se
ignoran porque requieren resolución de contexto que va más allá del AST.

Ticket: 2.1
Fecha: 2026-03-01
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class DependencyGraph:
    """
    Grafo dirigido de dependencias entre módulos internos del proyecto.

    Permite calcular Ca (Afferent Coupling) y Ce (Efferent Coupling) para
    cualquier módulo del proyecto.

    Attributes:
        outgoing: Mapa de módulo → conjunto de módulos internos que importa.
                  Incluye todas las cadenas de import internas, no solo las
                  que corresponden a archivos conocidos.
        known_modules: Conjunto de módulos internos con archivo .py en el proyecto.
    """

    outgoing: Dict[str, Set[str]] = field(default_factory=dict)
    known_modules: Set[str] = field(default_factory=set)

    def efferent_coupling(self, module: str) -> Set[str]:
        """
        Ce (Efferent Coupling): módulos internos de los que depende este módulo.

        Solo se cuentan módulos conocidos (con archivo .py en el proyecto).

        Args:
            module: Nombre de módulo dotted (ej: "quality_agents.codeguard.agent").

        Returns:
            Conjunto de nombres de módulos internos de los que depende.
        """
        deps = self.outgoing.get(module, set())
        return {d for d in deps if d in self.known_modules and d != module}

    def afferent_coupling(self, module: str) -> Set[str]:
        """
        Ca (Afferent Coupling): módulos internos que dependen de este módulo.

        Args:
            module: Nombre de módulo dotted.

        Returns:
            Conjunto de nombres de módulos internos que importan este módulo.
        """
        ca = set()
        for m, deps in self.outgoing.items():
            if m != module and module in deps and module in self.known_modules:
                ca.add(m)
        return ca

    @property
    def modules(self) -> Set[str]:
        """Retorna el conjunto de todos los módulos internos conocidos."""
        return set(self.known_modules)


class DependencyGraphBuilder:
    """
    Construye un DependencyGraph a partir de archivos Python del proyecto.

    Parsea cada archivo via AST para extraer sus imports absolutos, filtra
    los que son internos al proyecto (mismo root package) y construye el
    grafo de dependencias.

    Example:
        >>> builder = DependencyGraphBuilder()
        >>> files = list(Path("src").rglob("*.py"))
        >>> graph = builder.build(project_path, files)
        >>> ca = graph.afferent_coupling("quality_agents.shared.verifiable")
        >>> ce = graph.efferent_coupling("quality_agents.codeguard.agent")
    """

    def build(self, project_path: Path, files: List[Path]) -> DependencyGraph:
        """
        Construye el grafo de dependencias del proyecto.

        Args:
            project_path: Directorio raíz del proyecto.
            files: Lista de archivos Python a analizar.

        Returns:
            DependencyGraph con todos los módulos y sus dependencias.
        """
        python_files = [f for f in files if f.suffix == ".py"]

        # Paso 1: Construir mapa archivo → nombre de módulo
        file_to_module: Dict[Path, str] = {}
        for f in python_files:
            module_name = self._path_to_module(f, project_path)
            if module_name:
                file_to_module[f] = module_name

        known_modules: Set[str] = set(file_to_module.values())
        root_packages: Set[str] = {m.split(".")[0] for m in known_modules}

        # Paso 2: Construir aristas (outgoing edges)
        outgoing: Dict[str, Set[str]] = {m: set() for m in known_modules}

        for file_path, module_name in file_to_module.items():
            imports = self._extract_imports(file_path)
            for imp in imports:
                # Solo importaciones internas al proyecto
                if imp.split(".")[0] in root_packages:
                    outgoing[module_name].add(imp)

        return DependencyGraph(outgoing=outgoing, known_modules=known_modules)

    def _path_to_module(self, file_path: Path, project_path: Path) -> Optional[str]:
        """
        Convierte una ruta de archivo a su nombre de módulo dotted.

        Ejemplos:
            src/quality_agents/codeguard/agent.py  → quality_agents.codeguard.agent
            src/quality_agents/__init__.py          → quality_agents
            quality_agents/shared/config.py         → quality_agents.shared.config

        Args:
            file_path: Ruta al archivo Python.
            project_path: Directorio raíz del proyecto.

        Returns:
            Nombre de módulo dotted, o None si no puede calcularse.
        """
        try:
            relativa = file_path.relative_to(project_path)
        except ValueError:
            return file_path.stem

        partes = list(relativa.parts)

        # Quitar el directorio 'src' si está como primer componente
        if partes and partes[0] == "src":
            partes = partes[1:]

        if not partes:
            return None

        # Quitar extensión .py del último segmento
        partes[-1] = partes[-1].removesuffix(".py")

        # Quitar __init__ (el paquete se representa sin él)
        if partes[-1] == "__init__":
            partes = partes[:-1]

        return ".".join(partes) if partes else None

    def _extract_imports(self, file_path: Path) -> Set[str]:
        """
        Extrae los módulos importados por un archivo (solo imports absolutos).

        Args:
            file_path: Ruta al archivo Python.

        Returns:
            Conjunto de nombres de módulos importados.
        """
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return set()

        imports: Set[str] = set()

        for nodo in ast.walk(tree):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    imports.add(alias.name)
            elif isinstance(nodo, ast.ImportFrom):
                # level == 0: import absoluto
                if nodo.level == 0 and nodo.module:
                    imports.add(nodo.module)

        return imports
