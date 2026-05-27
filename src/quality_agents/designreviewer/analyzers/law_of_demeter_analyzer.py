"""
LawOfDemeterAnalyzer — Detección de violaciones a la Ley de Demeter.

La Ley de Demeter establece que un método solo debería hablar con sus "amigos
directos": self, sus parámetros, objetos que crea, y sus propios atributos.
Las cadenas de acceso del tipo `a.b.c` indican que el método sabe demasiado
sobre la estructura interna de otros objetos, creando acoplamiento estructural.

Viola OCP y el principio de encapsulamiento: si la estructura interna de `b`
cambia, este código se rompe aunque `a` no haya cambiado.

Condición de reporte:
    profundidad de cadena de atributos > max_demeter_depth  (default: 1)

Ejemplo problemático:  order.customer.address.city
Profundidad: 3 accesos encadenados sobre objetos intermedios.

Exclusiones:
    - Cadenas que comienzan con `self` (acceso a estado propio — legítimo)
    - Módulos/paquetes conocidos (stdlib y terceros usan fluent style)
"""

import ast
from pathlib import Path
from typing import Any, List, Union

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity, SolidPrinciple
from quality_agents.shared.verifiable import ExecutionContext, Verifiable


class LawOfDemeterAnalyzer(Verifiable):
    """
    Detecta cadenas de acceso a atributos que violan la Ley de Demeter.

    Recorre el AST buscando expresiones de la forma `a.b.c.d` cuya profundidad
    supere `max_demeter_depth`. Las cadenas que comienzan con `self` se excluyen
    porque representan acceso legítimo al estado propio del objeto.

    Severidad: WARNING.
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "LawOfDemeterAnalyzer"

    @property
    def category(self) -> str:
        return "smells"

    @property
    def estimated_duration(self) -> float:
        return 0.8

    @property
    def priority(self) -> int:
        return 4

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        if context.config and hasattr(context.config, "checks"):
            if not getattr(context.config.checks, "law_of_demeter", True):
                return False
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        results: List[ReviewResult] = []

        max_depth = 1
        if self._config is not None:
            max_depth = getattr(self._config, "max_demeter_depth", 1)

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return results

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._analizar_funcion(node, file_path, max_depth, results)

        return results

    def _analizar_funcion(
        self,
        func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        file_path: Path,
        max_depth: int,
        results: List[ReviewResult],
    ) -> None:
        """Busca cadenas de acceso que superan max_depth en el cuerpo de la función."""
        # Recolectar todos los nodos Attribute que son raíz de cadena
        # (es decir, cuyo padre NO es también un Attribute)
        cadenas_raiz = self._obtener_cadenas_raiz(func_node)

        for nodo in cadenas_raiz:
            cadena, depth = self._desplegar_cadena(nodo)
            if depth <= max_depth:
                continue
            # Excluir cadenas que comienzan con self
            if cadena and cadena[0] == "self":
                continue

            chain_str = ".".join(cadena)
            line = getattr(nodo, "lineno", None)

            context_name = func_node.name
            line_info = f" (línea {line})" if line else ""
            results.append(ReviewResult(
                analyzer_name=self.name,
                severity=ReviewSeverity.WARNING,
                current_value=depth,
                threshold=max_depth,
                message=(
                    f"Ley de Demeter: cadena '{chain_str}' tiene profundidad {depth} "
                    f"(máx {max_depth}) en '{context_name}'{line_info}. "
                    f"Viola encapsulamiento al acceder a estructura interna de objetos intermedios."
                ),
                file_path=file_path,
                class_name=context_name,
                suggestion=(
                    "Introducir un método en el objeto intermedio que devuelva "
                    "el valor necesario, evitando exponer su estructura interna."
                ),
                estimated_effort=0.5,
                solid_principle=SolidPrinciple.OCP,
                smell_type="LawOfDemeter",
            ))

    def _obtener_cadenas_raiz(
        self,
        func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> List[ast.Attribute]:
        """
        Retorna los nodos Attribute más externos de cada cadena.

        Un nodo Attribute es raíz si NO es el .value de otro Attribute,
        es decir, no hay ningún otro Attribute que lo use como base.
        Así se evita contar el mismo acceso múltiples veces al caminar el árbol.
        """
        todos = [n for n in ast.walk(func_node) if isinstance(n, ast.Attribute)]
        # IDs de nodos que son base (.value) de otro Attribute — son internos
        internos = {id(n.value) for n in todos if isinstance(n.value, ast.Attribute)}
        return [n for n in todos if id(n) not in internos]

    def _desplegar_cadena(self, nodo: ast.Attribute) -> tuple:
        """
        Recorre la cadena de Attribute hacia abajo y retorna (partes, profundidad).

        Ejemplo: para `a.b.c.d` retorna (["a", "b", "c", "d"], 3).
        La profundidad es el número de accesos encadenados (len - 1).
        """
        partes = []
        actual: Any = nodo

        while isinstance(actual, ast.Attribute):
            partes.append(actual.attr)
            actual = actual.value

        # actual es ahora el objeto base (Name, Call, etc.)
        if isinstance(actual, ast.Name):
            partes.append(actual.id)

        partes.reverse()
        depth = len(partes) - 1
        return partes, depth
