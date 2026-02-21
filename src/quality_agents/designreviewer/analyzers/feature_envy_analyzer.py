"""
FeatureEnvyAnalyzer — Detección de Feature Envy (envidia de atributos).

Un método tiene Feature Envy cuando accede más a los atributos y métodos de
un objeto externo (recibido como parámetro) que a los propios (self.X).
Esto sugiere que la lógica debería residir en la clase del objeto envidiado.

Viola el principio SRP: el método tiene más interés en los datos de otra clase
que en los de la propia, señal de que está en el lugar equivocado.

Solo se analiza en el contexto de métodos de clase (donde 'self' es significativo).
Los métodos dunder se excluyen para evitar falsos positivos en __init__, __eq__, etc.

Condición de reporte:
    accesos_param_max > accesos_self  AND  accesos_param_max >= MIN_ACCESOS_EXTERNOS

donde MIN_ACCESOS_EXTERNOS = 3 (evita falsos positivos en métodos con poco código).

Fecha de creación: 2026-02-20
Ticket: 4.4
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Set, Union

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity, SolidPrinciple
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

# Mínimo de accesos externos para considerar Feature Envy (evita falsos positivos)
_MIN_ACCESOS_EXTERNOS = 3

# Parámetros implícitos que se excluyen del análisis de Feature Envy
_PARAMS_IMPLICITOS: Set[str] = {"self", "cls"}


class FeatureEnvyAnalyzer(Verifiable):
    """
    Detecta métodos de clase con Feature Envy.

    Un método tiene Feature Envy si accede con mayor frecuencia a atributos
    o métodos de un objeto externo (parámetro) que a los propios (self.X).

    El análisis cuenta ocurrencias de la forma `nombre.algo` en el cuerpo del
    método, comparando las referencias a `self` contra las referencias al
    parámetro más accedido. Se reporta cuando:

        accesos_param_max > accesos_self  AND  accesos_param_max >= 3

    Umbral mínimo de 3 accesos externos para filtrar métodos triviales donde
    una sola llamada como `other.run()` generaría ruido innecesario.

    Severidad: WARNING (viola SRP).
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "FeatureEnvyAnalyzer"

    @property
    def category(self) -> str:
        return "smells"

    @property
    def estimated_duration(self) -> float:
        return 0.8

    @property
    def priority(self) -> int:
        return 3

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        return not context.is_excluded and context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[ReviewResult]:
        """
        Analiza el archivo y retorna un resultado por cada método con Feature Envy.

        Solo analiza métodos definidos dentro de clases (no funciones de módulo).

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

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._analizar_clase(node, file_path, results)

        return results

    def _analizar_clase(
        self,
        class_node: ast.ClassDef,
        file_path: Path,
        results: List[ReviewResult],
    ) -> None:
        """Analiza todos los métodos de instancia de una clase."""
        for nodo in class_node.body:
            if not isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if nodo.name.startswith("__"):
                continue  # Excluir dunder: __init__, __str__, etc.

            params_externos = self._obtener_params_externos(nodo)
            if not params_externos:
                continue  # Sin parámetros que envidiar

            accesos_self = self._contar_accesos(nodo, "self")
            accesos_por_param: Dict[str, int] = {
                p: self._contar_accesos(nodo, p) for p in params_externos
            }

            param_max = max(accesos_por_param, key=lambda p: accesos_por_param[p])
            max_accesos = accesos_por_param[param_max]

            if max_accesos > accesos_self and max_accesos >= _MIN_ACCESOS_EXTERNOS:
                nombre_metodo = f"{class_node.name}.{nodo.name}"
                results.append(ReviewResult(
                    analyzer_name=self.name,
                    severity=ReviewSeverity.WARNING,
                    current_value=max_accesos,
                    threshold=accesos_self,
                    message=(
                        f"Método '{nombre_metodo}' accede {max_accesos} veces a "
                        f"'{param_max}' vs {accesos_self} veces a self. "
                        f"Posible Feature Envy."
                    ),
                    file_path=file_path,
                    class_name=class_node.name,
                    suggestion=(
                        f"Mover '{nodo.name}' a la clase de '{param_max}', "
                        f"o extraer la lógica envidiada a una función auxiliar."
                    ),
                    estimated_effort=1.5,
                    solid_principle=SolidPrinciple.SRP,
                    smell_type="FeatureEnvy",
                ))

    def _obtener_params_externos(self, func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> List[str]:
        """
        Retorna los nombres de parámetros de la función excluyendo self y cls.

        Solo considera parámetros posicionales y keyword; excluye *args y **kwargs
        porque no representan objetos concretos que se puedan "envidiar".
        """
        args = func_node.args
        todos = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
        return [a.arg for a in todos if a.arg not in _PARAMS_IMPLICITOS]

    def _contar_accesos(self, func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef], nombre: str) -> int:
        """
        Cuenta las ocurrencias de `nombre.algo` en el cuerpo del método.

        Detecta tanto acceso a atributos (`param.x`) como llamadas a métodos
        (`param.method()`) ya que ambos representan uso de la interfaz del objeto.
        """
        count = 0
        for nodo in ast.walk(func_node):
            if (
                isinstance(nodo, ast.Attribute)
                and isinstance(nodo.value, ast.Name)
                and nodo.value.id == nombre
            ):
                count += 1
        return count
