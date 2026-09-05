"""
FatInterfaceAnalyzer — Detección de interfaces "gordas" (violación a ISP).

Una interfaz gorda (ABC o Protocol con demasiados métodos abstractos) fuerza
a los implementadores a proveer métodos que no necesitan, violando el
Principio de Segregación de Interfaces (ISP): los clientes no deberían
depender de métodos que no usan.

Heurística de detección:
- Clases que heredan de ABC/abc.ABC, o declaran metaclass=ABCMeta:
  se cuentan los métodos decorados con @abstractmethod.
- Clases que heredan de Protocol/typing.Protocol: se cuentan todos los
  métodos declarados en el cuerpo (el contrato completo del protocolo).

Si el conteo supera max_abstract_methods se reporta WARNING; si lo duplica,
CRITICAL (mismo patrón de gradiente que ComplexityCheck en CodeGuard).

Fecha de creación: 2026-09-05
Ticket: Spike #59 → Issue #73
"""

import ast
from pathlib import Path
from typing import Any, List, Union

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity, SolidPrinciple
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

_FuncNode = Union[ast.FunctionDef, ast.AsyncFunctionDef]

_BASES_ABC = {"ABC"}
_BASES_PROTOCOL = {"Protocol"}


class FatInterfaceAnalyzer(Verifiable):
    """
    Detecta interfaces (ABC/Protocol) con demasiados métodos abstractos.

    Umbral por defecto: 5 (configurable vía max_abstract_methods en pyproject.toml).
    Severidad: WARNING si excede el umbral, CRITICAL si lo duplica.
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "FatInterfaceAnalyzer"

    @property
    def category(self) -> str:
        return "design"

    @property
    def estimated_duration(self) -> float:
        return 0.4

    @property
    def priority(self) -> int:
        return 3

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        if (
            context.config
            and hasattr(context.config, "checks")
            and not getattr(context.config.checks, "fat_interface", True)
        ):
            return False
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        """
        Analiza el archivo y retorna un resultado por cada interfaz gorda detectada.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista de ReviewResult (puede ser vacía si no hay violaciones).
        """
        threshold = self._config.max_abstract_methods if self._config else 5
        results: List[ReviewResult] = []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            return results

        for nodo in ast.walk(tree):
            if not isinstance(nodo, ast.ClassDef):
                continue

            metodos_contrato = self._metodos_de_contrato(nodo)
            if metodos_contrato is None:
                continue  # No es ABC ni Protocol

            count = len(metodos_contrato)
            if count <= threshold:
                continue

            severity = ReviewSeverity.CRITICAL if count > threshold * 2 else ReviewSeverity.WARNING
            exceso = count - threshold

            results.append(ReviewResult(
                analyzer_name=self.name,
                severity=severity,
                current_value=count,
                threshold=threshold,
                message=(
                    f"Interfaz '{nodo.name}' tiene {count} métodos abstractos "
                    f"(umbral: {threshold}): fuerza a los implementadores a proveer "
                    f"métodos que pueden no necesitar."
                ),
                file_path=file_path,
                class_name=nodo.name,
                suggestion=(
                    f"Segregar '{nodo.name}' en 2 o más interfaces más pequeñas y "
                    f"cohesivas, agrupadas por el cliente que realmente usa cada grupo "
                    f"de métodos."
                ),
                estimated_effort=round(exceso * 1.0, 1),
                solid_principle=SolidPrinciple.ISP,
                smell_type="FatInterface",
            ))

        return results

    def _metodos_de_contrato(self, class_node: ast.ClassDef) -> Union[List[_FuncNode], None]:
        """
        Retorna los métodos que forman el contrato de la interfaz, o None si la
        clase no es una interfaz (ni ABC ni Protocol).

        Para ABC: solo los métodos decorados con @abstractmethod.
        Para Protocol: todos los métodos declarados en el cuerpo.
        """
        bases = {self._nombre_base(b) for b in class_node.bases}
        es_abc = bool(bases & _BASES_ABC) or self._tiene_metaclass_abc(class_node)
        es_protocol = bool(bases & _BASES_PROTOCOL)

        metodos = [
            n for n in class_node.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if es_protocol:
            return metodos

        if es_abc:
            return [m for m in metodos if self._tiene_decorador_abstractmethod(m)]

        # Clase que declara métodos @abstractmethod sin heredar explícitamente de ABC
        abstractos = [m for m in metodos if self._tiene_decorador_abstractmethod(m)]
        return abstractos if abstractos else None

    def _tiene_metaclass_abc(self, class_node: ast.ClassDef) -> bool:
        for kw in class_node.keywords:
            if kw.arg == "metaclass" and self._nombre_base(kw.value) == "ABCMeta":
                return True
        return False

    def _tiene_decorador_abstractmethod(self, func_node: _FuncNode) -> bool:
        for dec in func_node.decorator_list:
            nombre = dec.id if isinstance(dec, ast.Name) else self._nombre_base(dec)
            if nombre == "abstractmethod":
                return True
        return False

    def _nombre_base(self, nodo: ast.expr) -> str:
        """Extrae el nombre simple de un nodo (base de herencia o valor de keyword)."""
        if isinstance(nodo, ast.Name):
            return nodo.id
        if isinstance(nodo, ast.Attribute):
            return nodo.attr
        return ""
