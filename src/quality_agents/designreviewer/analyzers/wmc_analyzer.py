"""
WMCAnalyzer — Weighted Methods per Class.

Detecta clases con complejidad ciclomática total excesiva sumando la CC de
todos sus métodos (WMC = ∑ CC(método)). Una clase con WMC alto acumula
demasiada lógica, violando el Principio de Responsabilidad Única (SRP).

Usa radon para calcular la complejidad ciclomática de cada método.

Fecha de creación: 2026-02-20
Ticket: 3.2 + 3.5
"""

from pathlib import Path
from typing import Any, Dict, List

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

try:
    from radon.complexity import cc_visit  # type: ignore[import-untyped]
    from radon.visitors import Class as RadonClass  # type: ignore[import-untyped]

    _RADON_DISPONIBLE = True
except ImportError:
    _RADON_DISPONIBLE = False


class WMCAnalyzer(Verifiable):
    """
    Detecta clases con complejidad total excesiva (WMC alto).

    WMC (Weighted Methods per Class) = suma de la complejidad ciclomática
    de todos los métodos de la clase, calculada con radon.

    - WMC ≤ 20 → aceptable
    - WMC > 20 → la clase hace demasiado; candidata a extracción de métodos
                 o división en clases con responsabilidades acotadas

    Umbral por defecto: 20 (configurable vía max_wmc en pyproject.toml).
    Severidad: CRITICAL.
    """

    def __init__(self) -> None:
        self._config: Any = None

    @property
    def name(self) -> str:
        return "WMCAnalyzer"

    @property
    def category(self) -> str:
        return "cohesion"

    @property
    def estimated_duration(self) -> float:
        return 1.0

    @property
    def priority(self) -> int:
        return 2

    def should_run(self, context: ExecutionContext) -> bool:
        self._config = context.config
        return (
            _RADON_DISPONIBLE
            and not context.is_excluded
            and context.file_path.suffix == ".py"
        )

    def execute(self, file_path: Path) -> List[ReviewResult]:
        """
        Analiza el archivo y retorna un resultado por cada clase con WMC excesivo.

        Args:
            file_path: Ruta al archivo Python a analizar.

        Returns:
            Lista de ReviewResult (puede ser vacía si no hay violaciones).
        """
        threshold = self._config.max_wmc if self._config else 20
        results: List[ReviewResult] = []

        try:
            source = file_path.read_text(encoding="utf-8")
        except OSError:
            return results

        wmc_por_clase = self._calcular_wmc(source)

        for clase, wmc in wmc_por_clase.items():
            if wmc > threshold:
                exceso = wmc - threshold
                estimated_effort = round(exceso * 0.3, 1)

                results.append(ReviewResult(
                    analyzer_name=self.name,
                    severity=ReviewSeverity.CRITICAL,
                    current_value=wmc,
                    threshold=threshold,
                    message=(
                        f"Clase '{clase}' tiene WMC={wmc} "
                        f"(umbral: {threshold}): complejidad total de métodos excesiva."
                    ),
                    file_path=file_path,
                    class_name=clase,
                    suggestion=(
                        f"Reducir la complejidad total extrayendo {exceso} punto(s) de CC: "
                        f"simplificar métodos complejos, extraer clases auxiliares "
                        f"o aplicar patrones como Strategy para las ramas condicionales."
                    ),
                    estimated_effort=estimated_effort,
                ))

        return results

    def _calcular_wmc(self, source: str) -> Dict[str, int]:
        """
        Calcula el WMC de cada clase en el código fuente.

        Usa radon para obtener la complejidad ciclomática de cada método
        y la agrupa por clase (classname del bloque Function).

        Args:
            source: Código fuente Python como string.

        Returns:
            Diccionario {nombre_clase: wmc_total}.
        """
        wmc: Dict[str, int] = {}

        try:
            bloques = cc_visit(source)
        except Exception:
            return wmc

        for bloque in bloques:
            if isinstance(bloque, RadonClass):
                wmc[bloque.name] = sum(m.complexity for m in bloque.methods)

        return wmc
