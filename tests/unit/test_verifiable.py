"""
Tests unitarios para el módulo shared.verifiable.

Verifica el funcionamiento de:
- ExecutionContext (dataclass)
- Verifiable (clase base abstracta)

Fecha de creación: 2026-02-03
Ticket: 1.5.1
"""

from pathlib import Path
from typing import Any, List

import pytest

from quality_agents.shared.verifiable import ExecutionContext, Verifiable

# ========== Tests de ExecutionContext ==========


def test_execution_context_creation():
    """Verifica que ExecutionContext se puede crear con los campos requeridos."""
    file_path = Path("/test/file.py")
    context = ExecutionContext(file_path=file_path)

    assert context.file_path == file_path
    assert context.is_new_file is False
    assert context.is_modified is True
    assert context.analysis_type == "full"
    assert context.time_budget is None
    assert context.config is None
    assert context.is_excluded is False
    assert context.ai_enabled is False
    assert context.ai_suggestions is None


def test_execution_context_custom_values():
    """Verifica que ExecutionContext acepta valores personalizados."""
    file_path = Path("/test/new_file.py")
    config_mock = {"check_pep8": True}
    suggestions = ["Use type hints", "Add docstring"]

    context = ExecutionContext(
        file_path=file_path,
        is_new_file=True,
        is_modified=False,
        analysis_type="pre-commit",
        time_budget=5.0,
        config=config_mock,
        is_excluded=False,
        ai_enabled=True,
        ai_suggestions=suggestions,
    )

    assert context.file_path == file_path
    assert context.is_new_file is True
    assert context.is_modified is False
    assert context.analysis_type == "pre-commit"
    assert context.time_budget == 5.0
    assert context.config == config_mock
    assert context.is_excluded is False
    assert context.ai_enabled is True
    assert context.ai_suggestions == suggestions


def test_execution_context_all_analysis_types():
    """Verifica que ExecutionContext soporta todos los tipos de análisis."""
    analysis_types = ["pre-commit", "pr-review", "full", "sprint-end"]

    for analysis_type in analysis_types:
        context = ExecutionContext(
            file_path=Path("/test/file.py"), analysis_type=analysis_type
        )
        assert context.analysis_type == analysis_type


# ========== Tests de Verifiable ==========


class ConcreteVerifiable(Verifiable):
    """Implementación concreta de Verifiable para tests."""

    @property
    def name(self) -> str:
        return "TestCheck"

    @property
    def category(self) -> str:
        return "test"

    def execute(self, file_path: Path) -> List[Any]:
        return [{"check": "test", "file": str(file_path)}]


def test_verifiable_cannot_be_instantiated():
    """Verifica que Verifiable es abstracta y no puede instanciarse."""
    with pytest.raises(TypeError):
        Verifiable()  # type: ignore


def test_verifiable_concrete_implementation():
    """Verifica que una implementación concreta funciona correctamente."""
    verifiable = ConcreteVerifiable()

    assert verifiable.name == "TestCheck"
    assert verifiable.category == "test"
    assert verifiable.estimated_duration == 1.0  # default
    assert verifiable.priority == 5  # default


def test_verifiable_default_estimated_duration():
    """Verifica que estimated_duration tiene valor default correcto."""
    verifiable = ConcreteVerifiable()
    assert verifiable.estimated_duration == 1.0


def test_verifiable_default_priority():
    """Verifica que priority tiene valor default correcto."""
    verifiable = ConcreteVerifiable()
    assert verifiable.priority == 5


def test_verifiable_should_run_default_behavior():
    """Verifica que should_run default retorna True si no está excluido."""
    verifiable = ConcreteVerifiable()
    context = ExecutionContext(file_path=Path("/test/file.py"), is_excluded=False)

    assert verifiable.should_run(context) is True


def test_verifiable_should_run_excluded_file():
    """Verifica que should_run default retorna False si está excluido."""
    verifiable = ConcreteVerifiable()
    context = ExecutionContext(file_path=Path("/test/file.py"), is_excluded=True)

    assert verifiable.should_run(context) is False


def test_verifiable_execute_method():
    """Verifica que execute funciona en implementación concreta."""
    verifiable = ConcreteVerifiable()
    file_path = Path("/test/sample.py")

    results = verifiable.execute(file_path)

    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["check"] == "test"
    assert results[0]["file"] == str(file_path)


# ========== Tests de Verifiable con propiedades sobrescritas ==========


class CustomVerifiable(Verifiable):
    """Verifiable con propiedades personalizadas para tests."""

    @property
    def name(self) -> str:
        return "CustomCheck"

    @property
    def category(self) -> str:
        return "security"

    @property
    def estimated_duration(self) -> float:
        return 2.5

    @property
    def priority(self) -> int:
        return 1  # Alta prioridad

    def should_run(self, context: ExecutionContext) -> bool:
        # Lógica personalizada: solo archivos Python en pre-commit
        if context.is_excluded:
            return False
        if context.file_path.suffix != ".py":
            return False
        return context.analysis_type == "pre-commit"

    def execute(self, file_path: Path) -> List[Any]:
        return [{"custom": True}]


def test_verifiable_custom_estimated_duration():
    """Verifica que estimated_duration puede sobrescribirse."""
    verifiable = CustomVerifiable()
    assert verifiable.estimated_duration == 2.5


def test_verifiable_custom_priority():
    """Verifica que priority puede sobrescribirse."""
    verifiable = CustomVerifiable()
    assert verifiable.priority == 1


def test_verifiable_custom_should_run_logic():
    """Verifica que should_run puede tener lógica personalizada."""
    verifiable = CustomVerifiable()

    # Caso 1: archivo Python en pre-commit → True
    context1 = ExecutionContext(
        file_path=Path("/test/file.py"),
        analysis_type="pre-commit",
        is_excluded=False,
    )
    assert verifiable.should_run(context1) is True

    # Caso 2: archivo Python en full → False (no es pre-commit)
    context2 = ExecutionContext(
        file_path=Path("/test/file.py"), analysis_type="full", is_excluded=False
    )
    assert verifiable.should_run(context2) is False

    # Caso 3: archivo no-Python en pre-commit → False
    context3 = ExecutionContext(
        file_path=Path("/test/file.txt"),
        analysis_type="pre-commit",
        is_excluded=False,
    )
    assert verifiable.should_run(context3) is False

    # Caso 4: archivo excluido → False
    context4 = ExecutionContext(
        file_path=Path("/test/file.py"),
        analysis_type="pre-commit",
        is_excluded=True,
    )
    assert verifiable.should_run(context4) is False


# ========== Tests de integración ==========


def test_verifiable_integration_with_context():
    """Test de integración: Verifiable + ExecutionContext."""
    verifiable = ConcreteVerifiable()
    context = ExecutionContext(
        file_path=Path("/test/app.py"),
        is_new_file=True,
        analysis_type="pre-commit",
        time_budget=5.0,
    )

    # Verificar que should_run funciona con el contexto
    should_run = verifiable.should_run(context)
    assert should_run is True

    # Ejecutar verificación
    results = verifiable.execute(context.file_path)
    assert isinstance(results, list)
    assert len(results) > 0
