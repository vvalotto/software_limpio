"""
CBOAnalyzer — Coupling Between Objects.

Cuenta cuántas clases externas distintas referencia cada clase del archivo analizado.
Un CBO alto indica que la clase depende de demasiados tipos externos (viola ISP / DIP).

Fecha de creación: 2026-02-19
Ticket: 2.1 + 2.4
"""

import ast
from pathlib import Path
from typing import Any, List, Optional, Set

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

# Tipos que no cuentan como acoplamiento externo
_TIPOS_EXCLUIDOS: Set[str] = {
    # Built-ins de Python
    "int", "str", "float", "bool", "bytes", "complex",
    "list", "dict", "set", "tuple", "frozenset",
    "None", "object", "type", "super",
    # Typing
    "Optional", "List", "Dict", "Set", "Tuple", "Union", "Any", "Type",
    "Callable", "Generator", "Iterator", "Iterable", "Sequence", "Mapping",
    "ClassVar", "Final", "Literal", "TypeVar", "Protocol", "Self",
    "overload", "cast",
    # Excepciones comunes
    "Exception", "ValueError", "TypeError", "RuntimeError", "KeyError",
    "IndexError", "AttributeError", "NotImplementedError", "OSError",
    "IOError", "StopIteration", "AssertionError",
    # Decoradores / descriptores
    "property", "classmethod", "staticmethod", "abstractmethod",
    "dataclass", "field",
    # ABC
    "ABC",
    # Parámetros especiales de métodos
    "self", "cls",
}


class CBOAnalyzer(Verifiable):
    """
    Detecta clases con acoplamiento excesivo (CBO alto).

    CBO (Coupling Between Objects) = número de clases externas distintas que
    referencia una clase. Se detectan:
      - Clases base (herencia)
      - Type hints en parámetros, retornos y atributos de instancia
      - Instanciaciones directas: SomeClass(...)

    Umbral por defecto: 5 (configurable vía max_cbo en pyproject.toml).
    Severidad: CRITICAL.
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "CBOAnalyzer"

    @property
    def category(self) -> str:
        return "coupling"

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
        Analiza el archivo y retorna un resultado por cada clase con CBO excesivo.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista de ReviewResult (puede ser vacía si no hay violaciones).
        """
        threshold = self._config.max_cbo if self._config else 5
        results: List[ReviewResult] = []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return results

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            tipos_acoplados = self._calcular_cbo(node)
            cbo = len(tipos_acoplados)

            if cbo > threshold:
                exceso = cbo - threshold
                estimated_effort = round(exceso * 0.5, 1)

                results.append(ReviewResult(
                    analyzer_name=self.name,
                    severity=ReviewSeverity.CRITICAL,
                    current_value=cbo,
                    threshold=threshold,
                    message=(
                        f"Clase '{node.name}' tiene CBO={cbo} "
                        f"(umbral: {threshold}). "
                        f"Clases acopladas: {', '.join(sorted(tipos_acoplados))}."
                    ),
                    file_path=file_path,
                    class_name=node.name,
                    suggestion=(
                        f"Reducir dependencias directas aplicando Dependency Inversion: "
                        f"introducir interfaces/protocolos para las {exceso} clase(s) extra."
                    ),
                    estimated_effort=estimated_effort,
                ))

        return results

    def _calcular_cbo(self, class_node: ast.ClassDef) -> Set[str]:
        """Recolecta el conjunto de tipos externos que referencia la clase."""
        tipos: Set[str] = set()

        # 1. Clases base (herencia)
        for base in class_node.bases:
            nombre = self._extraer_nombre(base)
            if nombre and nombre not in _TIPOS_EXCLUIDOS:
                tipos.add(nombre)

        # 2. Recorrer el cuerpo de la clase
        for nodo in ast.walk(class_node):
            # 2a. Anotaciones de variables: attr: Tipo = ...
            if isinstance(nodo, ast.AnnAssign):
                tipos.update(self._nombres_de_anotacion(nodo.annotation))

            # 2b. Anotaciones de funciones (params + retorno)
            elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for arg in (
                    nodo.args.args
                    + nodo.args.posonlyargs
                    + nodo.args.kwonlyargs
                ):
                    if arg.annotation:
                        tipos.update(self._nombres_de_anotacion(arg.annotation))
                if nodo.returns:
                    tipos.update(self._nombres_de_anotacion(nodo.returns))

            # 2c. Instanciaciones: AlgunaClase(...)
            elif isinstance(nodo, ast.Call):
                nombre = self._extraer_nombre(nodo.func)
                if (
                    nombre
                    and nombre not in _TIPOS_EXCLUIDOS
                    and nombre[0].isupper()  # convencion: clases empiezan con mayúscula
                ):
                    tipos.add(nombre)

        return tipos

    def _nombres_de_anotacion(self, nodo: ast.expr) -> Set[str]:
        """Extrae nombres de tipos de un nodo de anotación."""
        nombres: Set[str] = set()

        if isinstance(nodo, ast.Name):
            if nodo.id not in _TIPOS_EXCLUIDOS:
                nombres.add(nodo.id)
        elif isinstance(nodo, ast.Attribute):
            nombre = self._extraer_nombre(nodo)
            if nombre and nombre not in _TIPOS_EXCLUIDOS:
                nombres.add(nombre)
        elif isinstance(nodo, ast.Subscript):
            # Ej: List[SomeType], Optional[SomeType]
            nombres.update(self._nombres_de_anotacion(nodo.value))
            nombres.update(self._nombres_de_anotacion(nodo.slice))
        elif isinstance(nodo, ast.BinOp):
            # Ej: SomeType | None (union syntax Python 3.10+)
            nombres.update(self._nombres_de_anotacion(nodo.left))
            nombres.update(self._nombres_de_anotacion(nodo.right))
        elif isinstance(nodo, ast.Tuple):
            for elt in nodo.elts:
                nombres.update(self._nombres_de_anotacion(elt))

        return nombres

    def _extraer_nombre(self, nodo: ast.expr) -> Optional[str]:
        """Extrae el nombre de un nodo Name o Attribute."""
        if isinstance(nodo, ast.Name):
            return nodo.id
        if isinstance(nodo, ast.Attribute):
            return nodo.attr  # retorna solo la parte final (ej: 'Config' de 'app.Config')
        return None
