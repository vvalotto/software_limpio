"""
LCOMAnalyzer — Lack of Cohesion of Methods.

Detecta clases con baja cohesión midiendo cuántos grupos desconectados de métodos
existen según los atributos de instancia que acceden. Una clase cohesiva tiene
todos sus métodos interrelacionados a través de atributos compartidos (LCOM = 1).

Implementa la variante LCOM4: número de componentes conexas en el grafo
método-atributo, donde dos métodos están conectados si acceden al menos un
atributo de instancia (self.X) en común.

Fecha de creación: 2026-02-20
Ticket: 3.1 + 3.5
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Set

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

# Decoradores que indican que el método no es de instancia
_DECORADORES_NO_INSTANCIA: Set[str] = {"staticmethod", "classmethod", "abstractmethod"}


class LCOMAnalyzer(Verifiable):
    """
    Detecta clases con baja cohesión (LCOM alto).

    LCOM4 (Lack of Cohesion of Methods) = número de componentes conexas en el
    grafo donde los nodos son métodos de instancia y las aristas conectan métodos
    que acceden al menos un atributo de instancia (self.X) en común.

    - LCOM = 1 → clase cohesiva (todos los métodos relacionados)
    - LCOM > 1 → clase debería dividirse en LCOM clases separadas

    Solo se consideran métodos que acceden al menos un self.X. Los métodos sin
    acceso a atributos de instancia (utilities puras) se excluyen del cálculo.

    Umbral por defecto: 1 (configurable vía max_lcom en pyproject.toml).
    Severidad: WARNING.
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "LCOMAnalyzer"

    @property
    def category(self) -> str:
        return "cohesion"

    @property
    def estimated_duration(self) -> float:
        return 0.5

    @property
    def priority(self) -> int:
        return 3

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        """
        Analiza el archivo y retorna un resultado por cada clase con LCOM excesivo.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista de ReviewResult (puede ser vacía si no hay violaciones).
        """
        threshold = self._config.max_lcom if self._config else 1
        results: List[ReviewResult] = []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return results

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            lcom = self._calcular_lcom(node)

            if lcom > threshold:
                exceso = lcom - threshold
                estimated_effort = round(exceso * 1.5, 1)

                results.append(ReviewResult(
                    analyzer_name=self.name,
                    severity=ReviewSeverity.WARNING,
                    current_value=lcom,
                    threshold=threshold,
                    message=(
                        f"Clase '{node.name}' tiene LCOM={lcom} "
                        f"(umbral: {threshold}): {lcom} grupos de métodos "
                        f"sin atributos compartidos."
                    ),
                    file_path=file_path,
                    class_name=node.name,
                    suggestion=(
                        f"Dividir '{node.name}' en {lcom} clases con responsabilidades "
                        f"bien definidas, una por cada grupo cohesivo de métodos."
                    ),
                    estimated_effort=estimated_effort,
                ))

        return results

    def _calcular_lcom(self, class_node: ast.ClassDef) -> int:
        """
        Calcula LCOM4 para la clase dada.

        1. Extrae el conjunto de atributos de instancia (self.X) que accede cada método.
        2. Considera solo métodos con al menos un atributo de instancia accedido.
        3. Construye el grafo de conectividad y cuenta las componentes conexas.

        Returns:
            Número de componentes conexas (LCOM4). Retorna 0 si la clase no tiene
            métodos de instancia con acceso a atributos.
        """
        atributos_por_metodo: Dict[str, Set[str]] = {}

        for nodo in class_node.body:
            if not isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if self._es_no_instancia(nodo):
                continue

            atributos = self._atributos_de_instancia(nodo)
            if atributos:  # Solo incluir métodos que acceden al menos un self.X
                atributos_por_metodo[nodo.name] = atributos

        if len(atributos_por_metodo) <= 1:
            return 0  # 0 o 1 métodos con atributos → cohesivo por definición

        return self._contar_componentes(atributos_por_metodo)

    def _es_no_instancia(self, func_node: ast.FunctionDef) -> bool:
        """Retorna True si el método es estático, de clase o abstracto sin cuerpo real."""
        for decorador in func_node.decorator_list:
            nombre = None
            if isinstance(decorador, ast.Name):
                nombre = decorador.id
            elif isinstance(decorador, ast.Attribute):
                nombre = decorador.attr
            if nombre in _DECORADORES_NO_INSTANCIA:
                return True
        return False

    def _atributos_de_instancia(self, func_node: ast.FunctionDef) -> Set[str]:
        """
        Extrae el conjunto de nombres de atributos de instancia (self.X) accedidos
        en el cuerpo del método.
        """
        atributos: Set[str] = set()

        for nodo in ast.walk(func_node):
            if (
                isinstance(nodo, ast.Attribute)
                and isinstance(nodo.value, ast.Name)
                and nodo.value.id == "self"
            ):
                atributos.add(nodo.attr)

        return atributos

    def _contar_componentes(self, atributos_por_metodo: Dict[str, Set[str]]) -> int:
        """
        Cuenta componentes conexas usando Union-Find.

        Dos métodos están en la misma componente si comparten al menos un atributo
        de instancia (directamente o a través de transitividad).
        """
        metodos = list(atributos_por_metodo.keys())
        parent: Dict[str, str] = {m: m for m in metodos}

        def find(x: str) -> str:
            while parent[x] != x:
                parent[x] = parent[parent[x]]  # compresión de camino
                x = parent[x]
            return x

        def union(x: str, y: str) -> None:
            parent[find(x)] = find(y)

        # Conectar métodos que comparten al menos un atributo
        for i, m1 in enumerate(metodos):
            for m2 in metodos[i + 1:]:
                if atributos_por_metodo[m1] & atributos_por_metodo[m2]:
                    union(m1, m2)

        # Contar raíces únicas = número de componentes
        return len({find(m) for m in metodos})
