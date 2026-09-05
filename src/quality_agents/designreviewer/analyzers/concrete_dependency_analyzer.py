"""
ConcreteDependencyAnalyzer — Detección de dependencias concretas (violación a DIP).

Una clase que instancia sus propios colaboradores en el constructor (en vez de
recibirlos inyectados) queda acoplada a implementaciones concretas y es difícil
de testear/sustituir — viola el Principio de Inversión de Dependencias (DIP).

Distinto de `LayerViolationsAnalyzer` (ArchitectAnalyst), que detecta DIP a
nivel macro (dirección de imports entre capas configuradas). Este analyzer
opera a nivel micro: dentro de una sola clase, sin necesidad de capas
configuradas.

Heurística de confianza baja-media (sin type hints, es una heurística AST,
no una prueba): dentro de `__init__`, se buscan asignaciones `self.x = Clase(...)`
donde `Clase` fue importada en el archivo y no es un tipo común de exclusión
(stdlib, builtins). Alto riesgo de falsos positivos — ver guía de usuario.

Fecha de creación: 2026-09-05
Ticket: Spike #59 → Issue #74
"""

import ast
from pathlib import Path
from typing import Any, List, Set

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity, SolidPrinciple
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

# Tipos comunes de stdlib/builtins que no cuentan como "dependencia concreta"
# a inyectar, aunque se importen explícitamente.
_TIPOS_EXCLUIDOS: Set[str] = {
    "Path", "PurePath",
    "datetime", "date", "time", "timedelta", "timezone",
    "Decimal", "UUID", "uuid4",
    "Enum", "IntEnum", "Flag", "IntFlag",
    "defaultdict", "OrderedDict", "Counter", "deque", "namedtuple",
    "dict", "list", "set", "tuple", "frozenset", "str", "int", "float", "bool",
}


class ConcreteDependencyAnalyzer(Verifiable):
    """
    Detecta clases que instancian demasiadas dependencias concretas en su constructor.

    Umbral por defecto: 2 (configurable vía max_concrete_dependencies en pyproject.toml).
    Instanciar 1-2 colaboradores concretos en el constructor es común y aceptable;
    3 o más sugiere que convendría inyectarlos.

    Severidad: WARNING (heurística de confianza baja-media, sin type hints).
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "ConcreteDependencyAnalyzer"

    @property
    def category(self) -> str:
        return "smells"

    @property
    def estimated_duration(self) -> float:
        return 0.5

    @property
    def priority(self) -> int:
        return 4

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        if (
            context.config
            and hasattr(context.config, "checks")
            and not getattr(context.config.checks, "concrete_dependency", True)
        ):
            return False
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        """
        Analiza el archivo y retorna un resultado por cada clase con dependencias
        concretas excesivas en su constructor.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista de ReviewResult (puede ser vacía si no hay violaciones).
        """
        threshold = self._config.max_concrete_dependencies if self._config else 2
        results: List[ReviewResult] = []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return results

        nombres_importados = self._extraer_nombres_importados(tree)
        if not nombres_importados:
            return results

        for nodo in ast.walk(tree):
            if not isinstance(nodo, ast.ClassDef):
                continue

            init = self._encontrar_init(nodo)
            if init is None:
                continue

            dependencias = self._dependencias_concretas(init, nombres_importados)
            count = len(dependencias)

            if count > threshold:
                exceso = count - threshold
                results.append(ReviewResult(
                    analyzer_name=self.name,
                    severity=ReviewSeverity.WARNING,
                    current_value=count,
                    threshold=threshold,
                    message=(
                        f"Clase '{nodo.name}' instancia {count} dependencias concretas "
                        f"en su constructor (umbral: {threshold}): {', '.join(sorted(dependencias))}. "
                        f"Heurística sin type hints — verificar antes de refactorizar."
                    ),
                    file_path=file_path,
                    class_name=nodo.name,
                    suggestion=(
                        f"Recibir {', '.join(sorted(dependencias))} como parámetros del "
                        f"constructor (inyección de dependencias), tipados contra una "
                        f"abstracción (Protocol/ABC) en vez de instanciarlos internamente."
                    ),
                    estimated_effort=round(exceso * 1.0, 1),
                    solid_principle=SolidPrinciple.DIP,
                    smell_type="ConcreteDependency",
                ))

        return results

    def _extraer_nombres_importados(self, tree: ast.AST) -> Set[str]:
        """Extrae los nombres locales de todo lo importado en el archivo."""
        nombres: Set[str] = set()
        for nodo in ast.walk(tree):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    nombres.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(nodo, ast.ImportFrom):
                for alias in nodo.names:
                    nombres.add(alias.asname or alias.name)
        return nombres

    def _encontrar_init(self, class_node: ast.ClassDef) -> ast.FunctionDef | None:
        for nodo in class_node.body:
            if isinstance(nodo, ast.FunctionDef) and nodo.name == "__init__":
                return nodo
        return None

    def _dependencias_concretas(
        self, init_node: ast.FunctionDef, nombres_importados: Set[str]
    ) -> Set[str]:
        """
        Retorna los nombres de clases importadas que se instancian y se asignan
        directamente a un atributo de instancia (self.x = Clase(...)) dentro de __init__.
        """
        dependencias: Set[str] = set()

        for nodo in ast.walk(init_node):
            if not isinstance(nodo, ast.Assign):
                continue
            if not self._asigna_a_self(nodo.targets):
                continue

            valor = nodo.value
            if not isinstance(valor, ast.Call) or not isinstance(valor.func, ast.Name):
                continue

            nombre_clase = valor.func.id
            if nombre_clase in nombres_importados and nombre_clase not in _TIPOS_EXCLUIDOS:
                dependencias.add(nombre_clase)

        return dependencias

    def _asigna_a_self(self, targets: List[ast.expr]) -> bool:
        return any(
            isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self"
            for t in targets
        )
