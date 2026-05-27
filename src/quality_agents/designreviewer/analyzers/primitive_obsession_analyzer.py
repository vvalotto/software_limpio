"""
PrimitiveObsessionAnalyzer — Detección de Primitive Obsession.

Primitive Obsession ocurre cuando se usan tipos primitivos (str, int, float, bool)
donde debería haber Value Objects, o cuando se agrupan múltiples primitivos del mismo
tipo en una firma de método, señal de que deberían encapsularse en una clase propia.

Dos patrones detectados:

1. N+ parámetros anotados con el mismo tipo primitivo en un método público.
   Ejemplo: create_point(x: float, y: float, z: float) → candidato a Point(x, y, z)

2. Parámetros de tipo dict / Dict en métodos públicos.
   Ejemplo: process(data: dict) → el dict probablemente debería ser una clase concreta.

Exclusiones:
    - Métodos dunder (__init__, __str__, etc.)
    - @classmethod y @staticmethod constructores con nombre "from_*" o "create_*"
    - Parámetros sin anotación de tipo (no se puede determinar el tipo)
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Union

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity, SolidPrinciple
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

_PRIMITIVOS = {"str", "int", "float", "bool", "bytes"}
_DICT_TIPOS = {"dict", "Dict"}


class PrimitiveObsessionAnalyzer(Verifiable):
    """
    Detecta métodos que usan primitivos donde deberían usarse Value Objects.

    Analiza firmas de métodos públicos buscando:
    - N+ parámetros del mismo tipo primitivo (configurable, default: 3)
    - Parámetros de tipo dict / Dict

    Severidad: WARNING.
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "PrimitiveObsessionAnalyzer"

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
            if not getattr(context.config.checks, "primitive_obsession", True):
                return False
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        results: List[ReviewResult] = []

        max_primitive_params = 3
        if self._config is not None:
            max_primitive_params = getattr(self._config, "max_primitive_params", 3)

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return results

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._analizar_clase(node, file_path, max_primitive_params, results)

        return results

    def _analizar_clase(
        self,
        class_node: ast.ClassDef,
        file_path: Path,
        max_primitive_params: int,
        results: List[ReviewResult],
    ) -> None:
        is_dataclass = self._es_dataclass(class_node)

        for nodo in class_node.body:
            if not isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            # Excluir dunder
            if nodo.name.startswith("__"):
                continue
            # Excluir métodos privados
            if nodo.name.startswith("_"):
                continue
            # Excluir __init__ de dataclasses
            if is_dataclass and nodo.name == "__init__":
                continue
            # Excluir constructores classmethods (from_*, create_*)
            if self._es_constructor_classmethod(nodo):
                continue

            nombre_metodo = f"{class_node.name}.{nodo.name}"
            params = self._obtener_params_anotados(nodo)

            self._verificar_primitivos_repetidos(
                params, nombre_metodo, max_primitive_params, file_path, results
            )
            self._verificar_dict_params(params, nombre_metodo, file_path, results)

    def _es_dataclass(self, class_node: ast.ClassDef) -> bool:
        """Retorna True si la clase tiene el decorador @dataclass."""
        for dec in class_node.decorator_list:
            if isinstance(dec, ast.Name) and dec.id == "dataclass":
                return True
            if isinstance(dec, ast.Attribute) and dec.attr == "dataclass":
                return True
        return False

    def _es_constructor_classmethod(
        self, func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> bool:
        """Retorna True si es un classmethod con nombre from_* o create_*."""
        es_classmethod = any(
            (isinstance(d, ast.Name) and d.id == "classmethod")
            for d in func_node.decorator_list
        )
        es_constructor = func_node.name.startswith("from_") or func_node.name.startswith("create_")
        return es_classmethod and es_constructor

    def _obtener_params_anotados(
        self, func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> Dict[str, str]:
        """
        Retorna {nombre_param: tipo_str} para parámetros con anotación de tipo,
        excluyendo self y cls.
        """
        params: Dict[str, str] = {}
        args = func_node.args
        todos = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)

        for arg in todos:
            if arg.arg in ("self", "cls"):
                continue
            if arg.annotation is None:
                continue
            tipo = self._extraer_nombre_tipo(arg.annotation)
            if tipo:
                params[arg.arg] = tipo

        return params

    def _extraer_nombre_tipo(self, annotation: ast.expr) -> str:
        """Extrae el nombre simple del tipo de una anotación AST."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        if isinstance(annotation, ast.Attribute):
            return annotation.attr
        # Para tipos genéricos como Dict[str, Any] extraemos el nombre base
        if isinstance(annotation, ast.Subscript):
            return self._extraer_nombre_tipo(annotation.value)
        return ""

    def _verificar_primitivos_repetidos(
        self,
        params: Dict[str, str],
        nombre_metodo: str,
        max_primitive_params: int,
        file_path: Path,
        results: List[ReviewResult],
    ) -> None:
        """Detecta N+ parámetros del mismo tipo primitivo."""
        conteo: Dict[str, List[str]] = {}
        for nombre, tipo in params.items():
            if tipo in _PRIMITIVOS:
                conteo.setdefault(tipo, []).append(nombre)

        for tipo, nombres in conteo.items():
            if len(nombres) >= max_primitive_params:
                results.append(ReviewResult(
                    analyzer_name=self.name,
                    severity=ReviewSeverity.WARNING,
                    current_value=len(nombres),
                    threshold=max_primitive_params,
                    message=(
                        f"Primitive Obsession: '{nombre_metodo}' tiene {len(nombres)} parámetros "
                        f"de tipo '{tipo}' ({', '.join(nombres)}). "
                        f"Considerar encapsularlos en un Value Object."
                    ),
                    file_path=file_path,
                    class_name=nombre_metodo,
                    suggestion=(
                        f"Crear una clase Value Object que agrupe los parámetros "
                        f"de tipo '{tipo}' con validación propia."
                    ),
                    estimated_effort=1.0,
                    solid_principle=SolidPrinciple.SRP,
                    smell_type="PrimitiveObsession",
                ))

    def _verificar_dict_params(
        self,
        params: Dict[str, str],
        nombre_metodo: str,
        file_path: Path,
        results: List[ReviewResult],
    ) -> None:
        """Detecta parámetros de tipo dict / Dict en métodos públicos."""
        dict_params = [n for n, t in params.items() if t in _DICT_TIPOS]

        for param in dict_params:
            results.append(ReviewResult(
                analyzer_name=self.name,
                severity=ReviewSeverity.WARNING,
                current_value=1,
                threshold=0,
                message=(
                    f"Primitive Obsession: '{nombre_metodo}' usa 'dict' en el parámetro "
                    f"'{param}'. Un dict genérico oculta la estructura real de los datos."
                ),
                file_path=file_path,
                class_name=nombre_metodo,
                suggestion=(
                    f"Reemplazar el parámetro '{param}: dict' por una clase "
                    f"con campos explícitos o un TypedDict."
                ),
                estimated_effort=0.5,
                solid_principle=SolidPrinciple.SRP,
                smell_type="PrimitiveObsession",
            ))
