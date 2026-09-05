"""
RefusedBequestAnalyzer — Detección de Refused Bequest (violación a LSP).

Refused Bequest ocurre cuando una subclase sobreescribe un método heredado
para vaciarlo o angostar su contrato (pass, ..., o levantar
NotImplementedError) mientras la clase base tiene una implementación real
para ese método. La subclase no puede sustituir a la base sin romper el
comportamiento esperado por quien llama al método — viola el Principio de
Sustitución de Liskov (LSP).

Heurística de confianza media: solo cubre el caso de contrato vaciado.
No detecta violaciones semánticas de LSP (precondiciones más fuertes,
postcondiciones más débiles, invariantes rotos), que requieren análisis de
tipos/contratos o IA.

Exclusiones:
- Métodos decorados con @abstractmethod.
- Clases que heredan de ABC/Protocol, o usan metaclass=ABCMeta: vaciar el
  método ahí es el contrato esperado, no una violación.
- Métodos dunder (incluye __init__).

Fecha de creación: 2026-09-05
Ticket: Spike #59 → Issue #72
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Union

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity, SolidPrinciple
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

_FuncNode = Union[ast.FunctionDef, ast.AsyncFunctionDef]

# Bases que marcan una clase como abstracta por convención (vaciar métodos ahí es esperado)
_BASES_ABSTRACTAS = {"ABC", "Protocol"}


class RefusedBequestAnalyzer(Verifiable):
    """
    Detecta subclases que vacían el contrato de un método heredado con implementación real.

    Para cada clase local con una base local, compara los métodos sobreescritos:
    si el cuerpo en la subclase es trivial (pass/.../raise NotImplementedError)
    y el cuerpo en la clase base es una implementación real, se reporta Refused
    Bequest.

    Severidad: WARNING (heurística de confianza media).
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "RefusedBequestAnalyzer"

    @property
    def category(self) -> str:
        return "inheritance"

    @property
    def estimated_duration(self) -> float:
        return 0.5

    @property
    def priority(self) -> int:
        return 3

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        if (
            context.config
            and hasattr(context.config, "checks")
            and not getattr(context.config.checks, "refused_bequest", True)
        ):
            return False
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        """
        Analiza el archivo y retorna un resultado por cada método con Refused Bequest.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista de ReviewResult (puede ser vacía si no hay violaciones).
        """
        results: List[ReviewResult] = []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return results

        clases = self._extraer_clases(tree)

        for nombre, class_node in clases.items():
            if self._es_clase_abstracta(class_node):
                continue

            for base_nombre in self._nombres_bases(class_node):
                base_node = clases.get(base_nombre)
                if base_node is None:
                    continue  # Base externa al archivo, no analizable
                if self._es_clase_abstracta(base_node):
                    continue

                self._comparar_metodos(nombre, class_node, base_node, file_path, results)

        return results

    def _comparar_metodos(
        self,
        nombre_clase: str,
        class_node: ast.ClassDef,
        base_node: ast.ClassDef,
        file_path: Path,
        results: List[ReviewResult],
    ) -> None:
        metodos_hijo = self._metodos(class_node)
        metodos_base = self._metodos(base_node)

        for metodo_nombre, metodo_hijo in metodos_hijo.items():
            if metodo_nombre.startswith("__") and metodo_nombre.endswith("__"):
                continue  # Excluir dunder (incluye __init__)
            if self._tiene_decorador_abstractmethod(metodo_hijo):
                continue

            metodo_base = metodos_base.get(metodo_nombre)
            if metodo_base is None:
                continue  # No sobreescribe nada, es un método nuevo

            if self._es_cuerpo_trivial(metodo_hijo.body) and not self._es_cuerpo_trivial(metodo_base.body):
                results.append(ReviewResult(
                    analyzer_name=self.name,
                    severity=ReviewSeverity.WARNING,
                    current_value=1,
                    threshold=0,
                    message=(
                        f"Método '{nombre_clase}.{metodo_nombre}' vacía el contrato heredado "
                        f"de '{base_node.name}.{metodo_nombre}' (Refused Bequest)."
                    ),
                    file_path=file_path,
                    class_name=nombre_clase,
                    suggestion=(
                        f"Si '{nombre_clase}' no puede cumplir el contrato de "
                        f"'{base_node.name}.{metodo_nombre}', evitar heredar de "
                        f"'{base_node.name}' y usar composición en su lugar."
                    ),
                    estimated_effort=2.0,
                    solid_principle=SolidPrinciple.LSP,
                    smell_type="RefusedBequest",
                ))

    def _extraer_clases(self, tree: ast.AST) -> Dict[str, ast.ClassDef]:
        """Extrae un mapa {nombre_clase: nodo} de las clases de nivel superior/anidadas."""
        clases: Dict[str, ast.ClassDef] = {}
        for nodo in ast.walk(tree):
            if isinstance(nodo, ast.ClassDef):
                clases[nodo.name] = nodo
        return clases

    def _nombres_bases(self, class_node: ast.ClassDef) -> List[str]:
        """Extrae los nombres de las clases base directas (sin filtrar)."""
        nombres = []
        for base in class_node.bases:
            nombre = self._nombre_base(base)
            if nombre:
                nombres.append(nombre)
        return nombres

    def _nombre_base(self, nodo: ast.expr) -> str:
        """Extrae el nombre simple de un nodo base de herencia."""
        if isinstance(nodo, ast.Name):
            return nodo.id
        if isinstance(nodo, ast.Attribute):
            return nodo.attr
        return ""

    def _es_clase_abstracta(self, class_node: ast.ClassDef) -> bool:
        """True si la clase hereda de ABC/Protocol o declara metaclass=ABCMeta."""
        if any(nombre in _BASES_ABSTRACTAS for nombre in self._nombres_bases(class_node)):
            return True
        for kw in class_node.keywords:
            if kw.arg == "metaclass" and self._nombre_base(kw.value) == "ABCMeta":
                return True
        return False

    def _metodos(self, class_node: ast.ClassDef) -> Dict[str, _FuncNode]:
        """Extrae {nombre_metodo: nodo} de los métodos definidos directamente en la clase."""
        metodos: Dict[str, _FuncNode] = {}
        for nodo in class_node.body:
            if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metodos[nodo.name] = nodo
        return metodos

    def _tiene_decorador_abstractmethod(self, func_node: _FuncNode) -> bool:
        for dec in func_node.decorator_list:
            nombre = self._nombre_base(dec) if not isinstance(dec, ast.Name) else dec.id
            if nombre == "abstractmethod":
                return True
        return False

    def _es_cuerpo_trivial(self, body: List[ast.stmt]) -> bool:
        """
        True si el cuerpo del método no hace nada más que declarar su docstring.

        Cuerpos triviales: `pass`, `...`, `raise NotImplementedError(...)`,
        opcionalmente precedidos de un docstring.
        """
        cuerpo = self._sin_docstring(body)

        if not cuerpo:
            return True
        if len(cuerpo) != 1:
            return False

        stmt = cuerpo[0]
        if isinstance(stmt, ast.Pass):
            return True
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
            return True
        if isinstance(stmt, ast.Raise):
            return self._es_raise_not_implemented(stmt)

        return False

    def _sin_docstring(self, body: List[ast.stmt]) -> List[ast.stmt]:
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            return body[1:]
        return body

    def _es_raise_not_implemented(self, stmt: ast.Raise) -> bool:
        exc = stmt.exc
        if exc is None:
            return False
        if isinstance(exc, ast.Call):
            exc = exc.func
        return isinstance(exc, ast.Name) and exc.id == "NotImplementedError"
