"""
Tests unitarios para CheckOrchestrator.

Verifica el funcionamiento de:
- Auto-discovery de checks
- Selección contextual de checks
- Estrategias (pre-commit, pr-review, ai-guided)
- Ordenamiento por prioridad

Fecha de creación: 2026-02-03
Ticket: 1.5.2
"""

from pathlib import Path
from typing import Any, List
from unittest.mock import Mock, patch

import pytest

from quality_agents.shared.verifiable import ExecutionContext, Verifiable
from quality_agents.codeguard.config import CodeGuardConfig
from quality_agents.codeguard.orchestrator import CheckOrchestrator


# ========== Mock Checks para Tests ==========


class FastCriticalCheck(Verifiable):
    """Check rápido y crítico para tests."""

    @property
    def name(self) -> str:
        return "FastCritical"

    @property
    def category(self) -> str:
        return "security"

    @property
    def estimated_duration(self) -> float:
        return 0.5

    @property
    def priority(self) -> int:
        return 1  # Crítico

    def execute(self, file_path: Path) -> List[Any]:
        return []


class MediumHighPriorityCheck(Verifiable):
    """Check de duración media y alta prioridad."""

    @property
    def name(self) -> str:
        return "MediumHigh"

    @property
    def category(self) -> str:
        return "style"

    @property
    def estimated_duration(self) -> float:
        return 1.5

    @property
    def priority(self) -> int:
        return 2  # Alta

    def execute(self, file_path: Path) -> List[Any]:
        return []


class SlowLowPriorityCheck(Verifiable):
    """Check lento y baja prioridad."""

    @property
    def name(self) -> str:
        return "SlowLow"

    @property
    def category(self) -> str:
        return "quality"

    @property
    def estimated_duration(self) -> float:
        return 3.0

    @property
    def priority(self) -> int:
        return 7  # Baja

    def execute(self, file_path: Path) -> List[Any]:
        return []


class ConditionalCheck(Verifiable):
    """Check que solo se ejecuta en ciertos contextos."""

    @property
    def name(self) -> str:
        return "Conditional"

    @property
    def category(self) -> str:
        return "test"

    @property
    def priority(self) -> int:
        return 3

    def should_run(self, context: ExecutionContext) -> bool:
        # Solo ejecutar en archivos Python no excluidos
        if context.is_excluded:
            return False
        return context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[Any]:
        return []


# ========== Tests de Inicialización ==========


def test_orchestrator_initialization():
    """Verifica que el orquestador se inicializa correctamente."""
    config = CodeGuardConfig()
    orchestrator = CheckOrchestrator(config)

    assert orchestrator.config == config
    assert isinstance(orchestrator.checks, list)
    # Ahora hay checks reales descubiertos (PEP8Check implementado en Fase 2)
    assert len(orchestrator.checks) >= 1  # Al menos PEP8Check
    # Verificar que PEP8Check fue descubierto
    assert any(c.name == "PEP8" for c in orchestrator.checks)


def test_orchestrator_discover_checks_module_not_found():
    """Verifica que _discover_checks encuentra checks reales del módulo."""
    config = CodeGuardConfig()
    orchestrator = CheckOrchestrator(config)

    # El módulo checks ahora existe con PEP8Check (Fase 2)
    assert len(orchestrator.checks) >= 1
    assert any(c.name == "PEP8" for c in orchestrator.checks)


# ========== Tests de Auto-Discovery con Mocks ==========


@patch("quality_agents.codeguard.orchestrator.importlib.import_module")
def test_discover_checks_with_mock_module(mock_import):
    """Verifica que auto-discovery encuentra y instancia checks correctamente."""
    # Crear mock del módulo checks
    mock_module = Mock()
    mock_module.__name__ = "quality_agents.codeguard.checks"

    # Configurar qué clases están en el módulo
    mock_module.FastCriticalCheck = FastCriticalCheck
    mock_module.MediumHighPriorityCheck = MediumHighPriorityCheck
    mock_module.SlowLowPriorityCheck = SlowLowPriorityCheck
    mock_module.Verifiable = Verifiable  # La clase base debe ser excluida

    # Configurar dir() para que retorne los nombres
    with patch("quality_agents.codeguard.orchestrator.dir") as mock_dir:
        mock_dir.return_value = [
            "FastCriticalCheck",
            "MediumHighPriorityCheck",
            "SlowLowPriorityCheck",
            "Verifiable",
            "some_function",  # Esto debe ser ignorado
            "_private",  # Esto debe ser ignorado
        ]

        mock_import.return_value = mock_module

        config = CodeGuardConfig()
        orchestrator = CheckOrchestrator(config)

        # Verificar que se descubrieron 3 checks (excluyendo Verifiable)
        assert len(orchestrator.checks) == 3
        assert any(c.name == "FastCritical" for c in orchestrator.checks)
        assert any(c.name == "MediumHigh" for c in orchestrator.checks)
        assert any(c.name == "SlowLow" for c in orchestrator.checks)


# ========== Tests de Selección de Checks ==========


def test_select_checks_empty_list():
    """Verifica que select_checks funciona con checks reales."""
    config = CodeGuardConfig()
    orchestrator = CheckOrchestrator(config)
    context = ExecutionContext(file_path=Path("test.py"))

    selected = orchestrator.select_checks(context)

    # Ahora hay checks reales (PEP8Check)
    assert len(selected) >= 1
    assert any(c.name == "PEP8" for c in selected)


def test_select_checks_with_manual_checks():
    """Verifica selección de checks con lista manual (bypass auto-discovery)."""
    config = CodeGuardConfig()
    orchestrator = CheckOrchestrator(config)

    # Agregar checks manualmente para testing
    orchestrator.checks = [
        FastCriticalCheck(),
        MediumHighPriorityCheck(),
        SlowLowPriorityCheck(),
    ]

    context = ExecutionContext(file_path=Path("test.py"), analysis_type="full")

    selected = orchestrator.select_checks(context)

    # En análisis full, todos los checks se seleccionan
    assert len(selected) == 3
    # Verificar que están ordenados por prioridad (1, 2, 7)
    assert selected[0].name == "FastCritical"
    assert selected[1].name == "MediumHigh"
    assert selected[2].name == "SlowLow"


def test_select_checks_respects_should_run():
    """Verifica que select_checks respeta el método should_run de cada check."""
    config = CodeGuardConfig()
    orchestrator = CheckOrchestrator(config)

    orchestrator.checks = [
        FastCriticalCheck(),
        ConditionalCheck(),  # Solo se ejecuta en archivos .py
    ]

    # Contexto con archivo .txt (ConditionalCheck debe ser excluido)
    context = ExecutionContext(file_path=Path("test.txt"), analysis_type="full")

    selected = orchestrator.select_checks(context)

    # Solo FastCriticalCheck debe estar seleccionado
    assert len(selected) == 1
    assert selected[0].name == "FastCritical"


def test_select_checks_excluded_file():
    """Verifica que checks con should_run default excluyen archivos excluidos."""
    config = CodeGuardConfig()
    orchestrator = CheckOrchestrator(config)

    orchestrator.checks = [FastCriticalCheck(), MediumHighPriorityCheck()]

    # Contexto con archivo excluido
    context = ExecutionContext(
        file_path=Path("test.py"), is_excluded=True, analysis_type="full"
    )

    selected = orchestrator.select_checks(context)

    # Ningún check debe ejecutarse (todos usan should_run default que verifica is_excluded)
    # Pero estos checks no sobrescriben should_run, usan el default de Verifiable
    # El default es: return not context.is_excluded
    assert len(selected) == 0


# ========== Tests de Estrategia Pre-Commit ==========


def test_select_for_precommit_filters_by_priority():
    """Verifica que pre-commit filtra por prioridad (solo 1-3)."""
    config = CodeGuardConfig()
    orchestrator = CheckOrchestrator(config)

    orchestrator.checks = [
        FastCriticalCheck(),  # priority=1
        MediumHighPriorityCheck(),  # priority=2
        SlowLowPriorityCheck(),  # priority=7 (debe ser excluido)
    ]

    context = ExecutionContext(
        file_path=Path("test.py"), analysis_type="pre-commit", time_budget=10.0
    )

    selected = orchestrator.select_checks(context)

    # Solo checks con prioridad 1-3
    assert len(selected) == 2
    assert selected[0].name == "FastCritical"
    assert selected[1].name == "MediumHigh"


def test_select_for_precommit_respects_time_budget():
    """Verifica que pre-commit respeta presupuesto de tiempo."""
    config = CodeGuardConfig()
    orchestrator = CheckOrchestrator(config)

    orchestrator.checks = [
        FastCriticalCheck(),  # 0.5s, priority=1
        MediumHighPriorityCheck(),  # 1.5s, priority=2
    ]

    # Presupuesto que solo permite el primer check
    context = ExecutionContext(
        file_path=Path("test.py"), analysis_type="pre-commit", time_budget=1.0
    )

    selected = orchestrator.select_checks(context)

    # Solo FastCriticalCheck cabe en 1.0s (MediumHigh necesita 1.5s)
    assert len(selected) == 1
    assert selected[0].name == "FastCritical"


def test_select_for_precommit_default_time_budget():
    """Verifica que pre-commit usa presupuesto default de 5s si no se especifica."""
    config = CodeGuardConfig()
    orchestrator = CheckOrchestrator(config)

    orchestrator.checks = [
        FastCriticalCheck(),  # 0.5s
        MediumHighPriorityCheck(),  # 1.5s
    ]

    # Sin especificar time_budget
    context = ExecutionContext(file_path=Path("test.py"), analysis_type="pre-commit")

    selected = orchestrator.select_checks(context)

    # Ambos checks caben en 5s (0.5 + 1.5 = 2.0s < 5.0s)
    assert len(selected) == 2


# ========== Tests de Estrategia PR-Review ==========


def test_select_for_pr_selects_all():
    """Verifica que pr-review selecciona todos los checks."""
    config = CodeGuardConfig()
    orchestrator = CheckOrchestrator(config)

    orchestrator.checks = [
        FastCriticalCheck(),
        MediumHighPriorityCheck(),
        SlowLowPriorityCheck(),
    ]

    context = ExecutionContext(file_path=Path("test.py"), analysis_type="pr-review")

    selected = orchestrator.select_checks(context)

    # Todos los checks seleccionados
    assert len(selected) == 3


# ========== Tests de Estrategia AI-Guided ==========


def test_select_with_ai_fallback():
    """Verifica que ai-guided hace fallback a selección completa (por ahora)."""
    config = CodeGuardConfig()
    orchestrator = CheckOrchestrator(config)

    orchestrator.checks = [FastCriticalCheck(), MediumHighPriorityCheck()]

    context = ExecutionContext(
        file_path=Path("test.py"), analysis_type="full", ai_enabled=True
    )

    selected = orchestrator.select_checks(context)

    # Por ahora, IA hace fallback a todos los checks
    assert len(selected) == 2


# ========== Tests de Ordenamiento ==========


def test_checks_ordered_by_priority():
    """Verifica que los checks seleccionados se ordenan por prioridad."""
    config = CodeGuardConfig()
    orchestrator = CheckOrchestrator(config)

    # Agregar en orden aleatorio
    orchestrator.checks = [
        SlowLowPriorityCheck(),  # priority=7
        FastCriticalCheck(),  # priority=1
        MediumHighPriorityCheck(),  # priority=2
    ]

    context = ExecutionContext(file_path=Path("test.py"), analysis_type="pr-review")

    selected = orchestrator.select_checks(context)

    # Verificar orden: 1, 2, 7
    assert len(selected) == 3
    assert selected[0].priority == 1
    assert selected[1].priority == 2
    assert selected[2].priority == 7
