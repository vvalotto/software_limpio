"""
DITAnalyzer — Depth of Inheritance Tree.

Detecta clases con jerarquías de herencia excesivamente profundas.
Un DIT alto implica que la clase hereda comportamiento de muchos niveles
intermedios, lo que dificulta entender, testear y mantener el código.

DIT se calcula dentro del archivo analizado. Las clases externas (de frameworks
o stdlib no visibles en el archivo) se cuentan como un nivel de profundidad.

Convención:
- Clase sin bases explícitas (hereda de object): DIT = 1
- Clase que extiende una clase externa desconocida: DIT = 2
- Clase que extiende una clase local de DIT=N: DIT = N + 1
- Herencia múltiple: se toma el máximo DIT de todas las bases

Fecha de creación: 2026-02-20
Ticket: 3.3 + 3.5
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Set

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable


class DITAnalyzer(Verifiable):
    """
    Detecta clases con árbol de herencia excesivamente profundo (DIT alto).

    DIT (Depth of Inheritance Tree) = número de niveles de herencia entre
    la clase y la raíz (object). Un DIT alto dificulta razonar sobre el
    comportamiento efectivo de la clase (herencia vs. composición).

    Umbral por defecto: 5 (configurable vía max_dit en pyproject.toml).
    Severidad: CRITICAL.
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "DITAnalyzer"

    @property
    def category(self) -> str:
        return "inheritance"

    @property
    def estimated_duration(self) -> float:
        return 0.5

    @property
    def priority(self) -> int:
        return 2

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        """
        Analiza el archivo y retorna un resultado por cada clase con DIT excesivo.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista de ReviewResult (puede ser vacía si no hay violaciones).
        """
        threshold = self._config.max_dit if self._config else 5
        results: List[ReviewResult] = []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return results

        clases_locales = self._extraer_clases(tree)
        if not clases_locales:
            return results

        memo: Dict[str, int] = {}
        for nombre in clases_locales:
            dit = self._calcular_dit(nombre, clases_locales, memo, set())

            if dit > threshold:
                exceso = dit - threshold
                estimated_effort = round(exceso * 2.0, 1)

                results.append(ReviewResult(
                    analyzer_name=self.name,
                    severity=ReviewSeverity.CRITICAL,
                    current_value=dit,
                    threshold=threshold,
                    message=(
                        f"Clase '{nombre}' tiene DIT={dit} "
                        f"(umbral: {threshold}): jerarquía de herencia excesivamente profunda."
                    ),
                    file_path=file_path,
                    class_name=nombre,
                    suggestion=(
                        f"Reemplazar los {exceso} nivel(es) extra de herencia por composición: "
                        f"extraer comportamiento compartido a clases auxiliares e inyectarlas, "
                        f"en lugar de heredar para reutilizar."
                    ),
                    estimated_effort=estimated_effort,
                ))

        return results

    def _extraer_clases(self, tree: ast.AST) -> Dict[str, List[str]]:
        """
        Extrae un mapa {nombre_clase: [nombres_de_bases]} del árbol AST.

        Solo considera clases de nivel superior o anidadas directamente
        en el módulo (no clases dentro de funciones).
        """
        clases: Dict[str, List[str]] = {}

        for nodo in ast.walk(tree):
            if not isinstance(nodo, ast.ClassDef):
                continue
            bases = [self._nombre_base(b) for b in nodo.bases]
            bases_filtradas = [b for b in bases if b and b != "object"]
            clases[nodo.name] = bases_filtradas

        return clases

    def _nombre_base(self, nodo: ast.expr) -> str:
        """Extrae el nombre simple de un nodo base de herencia."""
        if isinstance(nodo, ast.Name):
            return nodo.id
        if isinstance(nodo, ast.Attribute):
            return nodo.attr
        return ""

    def _calcular_dit(
        self,
        nombre: str,
        clases_locales: Dict[str, List[str]],
        memo: Dict[str, int],
        en_camino: Set[str],
    ) -> int:
        """
        Calcula el DIT de una clase mediante recursión con memoización.

        Args:
            nombre: Nombre de la clase a calcular.
            clases_locales: Mapa completo de clases del archivo.
            memo: Caché de resultados ya calculados.
            en_camino: Conjunto de clases en el camino actual (detección de ciclos).

        Returns:
            DIT de la clase.
        """
        if nombre in memo:
            return memo[nombre]

        # Ciclo de herencia (no debería ocurrir en Python válido, pero por seguridad)
        if nombre in en_camino:
            return 0

        # Clase externa al archivo → asumimos profundidad 1
        if nombre not in clases_locales:
            return 1

        bases = clases_locales[nombre]

        if not bases:
            # Sin bases explícitas → hereda de object directamente (DIT = 1)
            memo[nombre] = 1
            return 1

        nuevo_camino = en_camino | {nombre}
        max_base_dit = max(
            self._calcular_dit(base, clases_locales, memo, nuevo_camino)
            for base in bases
        )
        resultado = max_base_dit + 1
        memo[nombre] = resultado
        return resultado
