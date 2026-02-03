"""
Orquestador de checks para CodeGuard.

Este módulo implementa la selección inteligente de checks basada en contexto,
usando auto-discovery para encontrar todos los checks disponibles.

Fecha de creación: 2026-02-03
Ticket: 1.5.2
Basado en: docs/agentes/decision_arquitectura_checks_modulares.md
"""

import importlib
import inspect
import logging
from typing import List

from quality_agents.shared.verifiable import ExecutionContext, Verifiable
from quality_agents.codeguard.config import CodeGuardConfig

logger = logging.getLogger(__name__)


class CheckOrchestrator:
    """
    Orquesta la ejecución de checks basándose en contexto.

    El orquestador es responsable de:
    1. Auto-discovery de checks disponibles (busca clases que hereden de Verifiable)
    2. Selección contextual de qué checks ejecutar según análisis type
    3. Optimización de tiempo (respeta presupuestos)
    4. Ordenamiento por prioridad

    Estrategias de selección:
    - pre-commit: Solo checks rápidos (<2s) y alta prioridad (1-3)
    - pr-review: Todos los checks habilitados
    - full: Todos los checks
    - ai-guided: IA sugiere checks relevantes (futuro)

    Attributes:
        config: Configuración de CodeGuard
        checks: Lista de checks descubiertos automáticamente

    Example:
        >>> config = CodeGuardConfig()
        >>> orchestrator = CheckOrchestrator(config)
        >>> context = ExecutionContext(
        ...     file_path=Path("app.py"),
        ...     analysis_type="pre-commit",
        ...     time_budget=5.0
        ... )
        >>> checks_to_run = orchestrator.select_checks(context)
        >>> # Ejecutar checks seleccionados
    """

    def __init__(self, config: CodeGuardConfig):
        """
        Inicializa el orquestador.

        Args:
            config: Configuración de CodeGuard con umbrales y checks habilitados
        """
        self.config = config
        self.checks = self._discover_checks()
        logger.info(f"Orquestador inicializado con {len(self.checks)} checks descubiertos")

    def _discover_checks(self) -> List[Verifiable]:
        """
        Auto-discovery de checks en codeguard.checks.

        Busca todas las clases que heredan de Verifiable en el módulo checks,
        las instancia y retorna la lista.

        Returns:
            Lista de instancias de checks descubiertos

        Example:
            Si codeguard/checks/ contiene:
            - PEP8Check
            - PylintCheck
            - SecurityCheck

            Retorna: [PEP8Check(), PylintCheck(), SecurityCheck()]
        """
        checks = []

        try:
            # Importar el módulo checks
            checks_module = importlib.import_module("quality_agents.codeguard.checks")

            # Iterar sobre todos los atributos del módulo
            for name in dir(checks_module):
                obj = getattr(checks_module, name)

                # Verificar que sea una clase que hereda de Verifiable
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, Verifiable)
                    and obj is not Verifiable  # Excluir la clase base
                ):
                    try:
                        # Instanciar el check
                        check_instance = obj()
                        checks.append(check_instance)
                        logger.debug(f"Check descubierto: {check_instance.name}")
                    except Exception as e:
                        logger.warning(
                            f"Error al instanciar check {name}: {e}. Saltando."
                        )

        except ImportError:
            # El módulo checks aún no existe (normal en Fase 1.5)
            logger.info(
                "Módulo 'codeguard.checks' no encontrado. "
                "No hay checks disponibles todavía."
            )
        except Exception as e:
            logger.error(f"Error durante auto-discovery de checks: {e}")

        return checks

    def select_checks(self, context: ExecutionContext) -> List[Verifiable]:
        """
        Selecciona qué checks ejecutar basándose en el contexto.

        Aplica diferentes estrategias según el tipo de análisis:
        - pre-commit: Checks rápidos y críticos (presupuesto 5s)
        - pr-review: Todos los checks habilitados
        - full: Todos los checks
        - ai-enabled: Selección guiada por IA (futuro)

        Args:
            context: Contexto de ejecución con información del archivo y análisis

        Returns:
            Lista de checks seleccionados, ordenados por prioridad (1=primero)

        Example:
            >>> context = ExecutionContext(
            ...     file_path=Path("app.py"),
            ...     analysis_type="pre-commit",
            ...     time_budget=5.0
            ... )
            >>> selected = orchestrator.select_checks(context)
            >>> # Retorna solo checks rápidos y críticos
        """
        # Paso 1: Filtrar checks que deben ejecutarse según su lógica should_run()
        candidates = [check for check in self.checks if check.should_run(context)]

        logger.debug(
            f"Candidatos después de should_run(): {len(candidates)}/{len(self.checks)}"
        )

        # Paso 2: Aplicar estrategia según tipo de análisis
        if context.analysis_type == "pre-commit":
            selected = self._select_for_precommit(candidates, context)
        elif context.analysis_type == "pr-review":
            selected = self._select_for_pr(candidates, context)
        elif context.ai_enabled:
            selected = self._select_with_ai(candidates, context)
        else:
            # Full o cualquier otro tipo
            selected = candidates

        # Paso 3: Ordenar por prioridad (1=más alta primero)
        selected.sort(key=lambda c: c.priority)

        logger.info(
            f"Checks seleccionados: {len(selected)} "
            f"(tipo: {context.analysis_type}, "
            f"presupuesto: {context.time_budget}s)"
        )

        return selected

    def _select_for_precommit(
        self, candidates: List[Verifiable], context: ExecutionContext
    ) -> List[Verifiable]:
        """
        Estrategia pre-commit: solo checks rápidos y críticos.

        Criterios:
        - Prioridad: 1-3 (alta)
        - Duración: Respeta presupuesto de tiempo (default 5s)
        - Selección greedy por prioridad hasta agotar presupuesto

        Args:
            candidates: Checks candidatos (ya pasaron should_run)
            context: Contexto de ejecución (debe tener time_budget)

        Returns:
            Lista de checks seleccionados que caben en el presupuesto
        """
        # Presupuesto default para pre-commit: 5 segundos
        if context.time_budget is None:
            context.time_budget = 5.0

        selected = []
        time_used = 0.0

        # Ordenar candidatos por prioridad (1=más alta primero)
        sorted_candidates = sorted(candidates, key=lambda c: c.priority)

        for check in sorted_candidates:
            # Solo alta prioridad (1-3)
            if check.priority > 3:
                logger.debug(
                    f"Check {check.name} saltado (prioridad {check.priority} > 3)"
                )
                continue

            # Verificar si cabe en el presupuesto
            if time_used + check.estimated_duration <= context.time_budget:
                selected.append(check)
                time_used += check.estimated_duration
                logger.debug(
                    f"Check {check.name} seleccionado "
                    f"(prioridad={check.priority}, "
                    f"duración={check.estimated_duration}s, "
                    f"tiempo usado={time_used:.1f}s)"
                )
            else:
                logger.debug(
                    f"Check {check.name} saltado por presupuesto "
                    f"(necesita {check.estimated_duration}s, "
                    f"disponible {context.time_budget - time_used:.1f}s)"
                )
                # Ya no hay tiempo, terminar
                break

        logger.info(
            f"Pre-commit: {len(selected)}/{len(candidates)} checks "
            f"seleccionados ({time_used:.1f}s/{context.time_budget}s)"
        )

        return selected

    def _select_for_pr(
        self, candidates: List[Verifiable], context: ExecutionContext
    ) -> List[Verifiable]:
        """
        Estrategia PR review: todos los checks habilitados.

        En PR review no hay restricción de tiempo crítica,
        por lo que se ejecutan todos los checks que pasaron should_run().

        Args:
            candidates: Checks candidatos (ya pasaron should_run)
            context: Contexto de ejecución

        Returns:
            Todos los candidatos (sin filtro adicional)
        """
        logger.info(f"PR-review: {len(candidates)} checks seleccionados (todos)")
        return candidates

    def _select_with_ai(
        self, candidates: List[Verifiable], context: ExecutionContext
    ) -> List[Verifiable]:
        """
        Estrategia guiada por IA: selección inteligente basada en diff.

        Esta funcionalidad está planificada para una fase futura.
        La IA analizará el diff del archivo y sugerirá qué checks son relevantes.

        Ejemplos de lógica futura:
        - Solo cambios de formato → PEP8 + Imports
        - Nueva función compleja → Complejidad + Types + Security
        - Refactoring → Todos los checks
        - Cambios en tests → Types + Coverage

        Args:
            candidates: Checks candidatos (ya pasaron should_run)
            context: Contexto de ejecución (puede tener ai_suggestions)

        Returns:
            Lista de checks sugeridos por IA (por ahora, fallback a todos)

        Note:
            TODO: Implementar cuando se agregue integración con IA (Fase 3)
        """
        # TODO: Implementar selección guiada por IA
        # Por ahora, fallback a selección completa
        logger.info(
            f"AI-guided (fallback): {len(candidates)} checks seleccionados "
            "(IA no implementada todavía)"
        )
        return candidates
