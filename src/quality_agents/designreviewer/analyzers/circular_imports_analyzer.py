"""
CircularImportsAnalyzer — Detección de ciclos de importación.

Detecta ciclos directos (A importa B, B importa A) en el grafo de dependencias
entre los archivos Python del proyecto. Las importaciones circulares violan DIP
e indican acoplamiento bidireccional entre módulos.

Fecha de creación: 2026-02-19
Ticket: 2.3 + 2.4
"""

import ast
from pathlib import Path
from typing import Any, List, Optional, Set, Tuple

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable


class CircularImportsAnalyzer(Verifiable):
    """
    Detecta importaciones circulares directas entre módulos del proyecto.

    Un ciclo directo ocurre cuando:
        módulo A importa módulo B  Y  módulo B importa módulo A

    Algoritmo:
        1. Extraer los módulos importados por el archivo analizado
        2. Para cada módulo importado, localizar su archivo en el proyecto
        3. Verificar si ese archivo importa de vuelta al módulo original

    Solo analiza archivos dentro del mismo proyecto (no librerías externas).
    Severidad: CRITICAL.
    estimated_effort: 2.0 horas por ciclo (fijo).
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "CircularImportsAnalyzer"

    @property
    def category(self) -> str:
        return "coupling"

    @property
    def estimated_duration(self) -> float:
        return 1.0

    @property
    def priority(self) -> int:
        return 1  # Crítico — los ciclos rompen la inicialización

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        """
        Analiza el archivo y retorna un resultado por cada ciclo directo detectado.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista de ReviewResult (un resultado por ciclo).
        """
        results: List[ReviewResult] = []

        root = self._encontrar_raiz_proyecto(file_path)
        modulo_actual = self._archivo_a_modulo(file_path, root)
        imports_actuales = self._obtener_imports(file_path)

        for modulo_importado in imports_actuales:
            archivo_importado = self._modulo_a_archivo(modulo_importado, root)
            if archivo_importado is None or archivo_importado == file_path:
                continue

            # Verificar si el archivo importado nos importa de vuelta
            sus_imports = self._obtener_imports(archivo_importado)
            if modulo_actual and modulo_actual in sus_imports:
                results.append(ReviewResult(
                    analyzer_name=self.name,
                    severity=ReviewSeverity.CRITICAL,
                    current_value=1,
                    threshold=0,
                    message=(
                        f"Ciclo de importación directo: "
                        f"'{file_path.name}' ↔ '{archivo_importado.name}'. "
                        f"Ambos módulos se importan mutuamente."
                    ),
                    file_path=file_path,
                    suggestion=(
                        f"Romper el ciclo extrayendo las dependencias comunes a un "
                        f"tercer módulo, o invirtiendo una de las dependencias mediante "
                        f"una interfaz/protocolo."
                    ),
                    estimated_effort=2.0,
                ))

        return results

    # -------------------------------------------------------------------------
    # Métodos auxiliares
    # -------------------------------------------------------------------------

    def _encontrar_raiz_proyecto(self, file_path: Path) -> Path:
        """
        Sube por el árbol de directorios hasta encontrar la raíz del proyecto.

        Busca `pyproject.toml`, `setup.py` o `setup.cfg` como indicadores de raíz.
        Si no los encuentra, usa el directorio del archivo.

        Args:
            file_path: Ruta al archivo de origen.

        Returns:
            Directorio raíz del proyecto.
        """
        indicadores = {"pyproject.toml", "setup.py", "setup.cfg"}
        current = file_path.parent

        while current != current.parent:
            if any((current / ind).exists() for ind in indicadores):
                return current
            current = current.parent

        return file_path.parent

    def _archivo_a_modulo(self, file_path: Path, root: Path) -> Optional[str]:
        """
        Convierte una ruta de archivo a su nombre de módulo dotted.

        Ej: `/proyecto/src/quality_agents/agent.py` → `quality_agents.agent`

        Args:
            file_path: Ruta al archivo Python.
            root: Directorio raíz del proyecto.

        Returns:
            Nombre de módulo dotted, o None si no puede calcularse.
        """
        try:
            relativa = file_path.relative_to(root)
        except ValueError:
            return file_path.stem

        partes = list(relativa.parts)

        # Quitar el directorio 'src' si está como primer componente
        if partes and partes[0] == "src":
            partes = partes[1:]

        # Quitar extensión .py del último segmento
        if partes:
            partes[-1] = partes[-1].removesuffix(".py")
            # Quitar __init__ (representa el paquete mismo)
            if partes[-1] == "__init__":
                partes = partes[:-1]

        return ".".join(partes) if partes else None

    def _obtener_imports(self, file_path: Path) -> Set[str]:
        """
        Extrae todos los módulos importados por un archivo (solo imports absolutos).

        Retorna los nombres completos dotted de los módulos importados.
        Los imports relativos se ignoran.

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
                if nodo.level == 0 and nodo.module:
                    imports.add(nodo.module)

        return imports

    def _modulo_a_archivo(self, modulo: str, root: Path) -> Optional[Path]:
        """
        Intenta encontrar el archivo .py correspondiente a un nombre de módulo.

        Busca en el directorio raíz del proyecto y en el subdirectorio `src/`.

        Args:
            modulo: Nombre de módulo dotted (ej: `quality_agents.agent`).
            root: Directorio raíz del proyecto.

        Returns:
            Path al archivo si se encuentra, None en caso contrario.
        """
        ruta_relativa = Path(*modulo.split("."))
        bases_busqueda = [root, root / "src"]

        for base in bases_busqueda:
            # Intentar como módulo directo: quality_agents/agent.py
            candidato = base / ruta_relativa.with_suffix(".py")
            if candidato.exists():
                return candidato

            # Intentar como paquete: quality_agents/agent/__init__.py
            candidato = base / ruta_relativa / "__init__.py"
            if candidato.exists():
                return candidato

        return None

    def _detectar_ciclos_en_grafo(
        self, nodo: str, grafo: dict, visitados: Set[str], pila: List[str]
    ) -> List[Tuple[str, str]]:
        """
        DFS para detectar ciclos en el grafo de dependencias.

        Reservado para implementación futura de ciclos indirectos (N > 2).
        """
        ciclos = []
        visitados.add(nodo)
        pila.append(nodo)

        for vecino in grafo.get(nodo, []):
            if vecino not in visitados:
                ciclos.extend(
                    self._detectar_ciclos_en_grafo(vecino, grafo, visitados, pila)
                )
            elif vecino in pila:
                ciclos.append((nodo, vecino))

        pila.pop()
        return ciclos
