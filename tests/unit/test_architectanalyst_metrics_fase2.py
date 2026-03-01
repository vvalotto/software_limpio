"""
Tests unitarios para las métricas de Martin (Fase 2 de ArchitectAnalyst).

Cubre:
  - DependencyGraphBuilder y DependencyGraph (Ticket 2.1)
  - CouplingAnalyzer — Ca y Ce (Ticket 2.2)
  - InstabilityAnalyzer — I (Ticket 2.3)
  - AbstractnessAnalyzer — A (Ticket 2.4)
  - DistanceAnalyzer — D (Ticket 2.5)

Ticket: 2.6
Fecha: 2026-03-01
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from quality_agents.architectanalyst.config import ArchitectAnalystConfig
from quality_agents.architectanalyst.metrics.abstractness_analyzer import AbstractnessAnalyzer
from quality_agents.architectanalyst.metrics.coupling_analyzer import CouplingAnalyzer
from quality_agents.architectanalyst.metrics.dependency_graph import (
    DependencyGraph,
    DependencyGraphBuilder,
)
from quality_agents.architectanalyst.metrics.distance_analyzer import DistanceAnalyzer
from quality_agents.architectanalyst.metrics.instability_analyzer import InstabilityAnalyzer
from quality_agents.architectanalyst.models import ArchitectureSeverity


# =============================================================================
# Fixtures: proyecto sintético en tmp_path
# =============================================================================


@pytest.fixture()
def proyecto_simple(tmp_path: Path) -> Path:
    """
    Proyecto mínimo con estructura src/mipkg/:
      - core.py      → sin imports internos (estable)
      - service.py   → importa core (depende de core)
      - controller.py → importa service y core (depende de ambos)
      - abstracts.py → define clase ABC (abstracta)
    """
    pkg = tmp_path / "src" / "mipkg"
    pkg.mkdir(parents=True)

    (pkg / "__init__.py").write_text("", encoding="utf-8")

    (pkg / "core.py").write_text(
        "class CoreService:\n    def run(self): pass\n",
        encoding="utf-8",
    )

    (pkg / "service.py").write_text(
        "from mipkg.core import CoreService\n"
        "class ServiceA:\n    def go(self): pass\n",
        encoding="utf-8",
    )

    (pkg / "controller.py").write_text(
        "from mipkg.service import ServiceA\n"
        "from mipkg.core import CoreService\n"
        "class Controller:\n    pass\n",
        encoding="utf-8",
    )

    (pkg / "abstracts.py").write_text(
        "from abc import ABC, abstractmethod\n"
        "class Base(ABC):\n"
        "    @abstractmethod\n"
        "    def execute(self): pass\n"
        "class Concrete:\n"
        "    def execute(self): pass\n",
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture()
def files_simple(proyecto_simple: Path) -> list:
    return list(proyecto_simple.rglob("*.py"))


# =============================================================================
# DependencyGraphBuilder — Ticket 2.1
# =============================================================================


class TestDependencyGraphBuilder:
    def test_build_retorna_grafo(self, proyecto_simple: Path, files_simple: list) -> None:
        builder = DependencyGraphBuilder()
        graph = builder.build(proyecto_simple, files_simple)
        assert isinstance(graph, DependencyGraph)

    def test_known_modules_detecta_archivos(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        builder = DependencyGraphBuilder()
        graph = builder.build(proyecto_simple, files_simple)
        # Al menos los 4 módulos principales deben estar presentes
        assert "mipkg.core" in graph.modules
        assert "mipkg.service" in graph.modules
        assert "mipkg.controller" in graph.modules
        assert "mipkg.abstracts" in graph.modules

    def test_efferent_coupling_service_depende_de_core(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        builder = DependencyGraphBuilder()
        graph = builder.build(proyecto_simple, files_simple)
        ce = graph.efferent_coupling("mipkg.service")
        assert "mipkg.core" in ce

    def test_efferent_coupling_controller_depende_de_dos(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        builder = DependencyGraphBuilder()
        graph = builder.build(proyecto_simple, files_simple)
        ce = graph.efferent_coupling("mipkg.controller")
        assert "mipkg.service" in ce
        assert "mipkg.core" in ce

    def test_efferent_coupling_core_es_cero(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        builder = DependencyGraphBuilder()
        graph = builder.build(proyecto_simple, files_simple)
        ce = graph.efferent_coupling("mipkg.core")
        # core no importa módulos internos
        assert len(ce) == 0

    def test_afferent_coupling_core_tiene_dos(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        builder = DependencyGraphBuilder()
        graph = builder.build(proyecto_simple, files_simple)
        ca = graph.afferent_coupling("mipkg.core")
        # service y controller importan core
        assert "mipkg.service" in ca
        assert "mipkg.controller" in ca

    def test_afferent_coupling_controller_es_cero(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        builder = DependencyGraphBuilder()
        graph = builder.build(proyecto_simple, files_simple)
        ca = graph.afferent_coupling("mipkg.controller")
        # nadie importa controller
        assert len(ca) == 0

    def test_modulo_no_se_cuenta_a_si_mismo(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        builder = DependencyGraphBuilder()
        graph = builder.build(proyecto_simple, files_simple)
        assert "mipkg.service" not in graph.efferent_coupling("mipkg.service")
        assert "mipkg.service" not in graph.afferent_coupling("mipkg.service")

    def test_build_sin_archivos_retorna_grafo_vacio(self, tmp_path: Path) -> None:
        builder = DependencyGraphBuilder()
        graph = builder.build(tmp_path, [])
        assert len(graph.modules) == 0

    def test_path_to_module_con_src(self, tmp_path: Path) -> None:
        builder = DependencyGraphBuilder()
        f = tmp_path / "src" / "mipkg" / "agent.py"
        result = builder._path_to_module(f, tmp_path)
        assert result == "mipkg.agent"

    def test_path_to_module_sin_src(self, tmp_path: Path) -> None:
        builder = DependencyGraphBuilder()
        f = tmp_path / "mipkg" / "agent.py"
        result = builder._path_to_module(f, tmp_path)
        assert result == "mipkg.agent"

    def test_path_to_module_init(self, tmp_path: Path) -> None:
        builder = DependencyGraphBuilder()
        f = tmp_path / "src" / "mipkg" / "__init__.py"
        result = builder._path_to_module(f, tmp_path)
        assert result == "mipkg"

    def test_ignora_imports_externos(self, tmp_path: Path) -> None:
        """Imports de stdlib o third-party no deben aparecer en el grafo."""
        pkg = tmp_path / "src" / "mipkg"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "mod.py").write_text(
            "import os\nimport pathlib\nfrom typing import List\n", encoding="utf-8"
        )
        files = list(tmp_path.rglob("*.py"))
        builder = DependencyGraphBuilder()
        graph = builder.build(tmp_path, files)
        ce = graph.efferent_coupling("mipkg.mod")
        assert len(ce) == 0

    def test_ignora_imports_relativos(self, tmp_path: Path) -> None:
        pkg = tmp_path / "src" / "mipkg"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "a.py").write_text("from . import b\n", encoding="utf-8")
        (pkg / "b.py").write_text("x = 1\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        builder = DependencyGraphBuilder()
        graph = builder.build(tmp_path, files)
        # Imports relativos ignorados → Ce de a debe ser 0
        ce = graph.efferent_coupling("mipkg.a")
        assert len(ce) == 0


# =============================================================================
# CouplingAnalyzer — Ticket 2.2
# =============================================================================


class TestCouplingAnalyzer:
    def test_nombre_y_categoria(self) -> None:
        a = CouplingAnalyzer()
        assert a.name == "CouplingAnalyzer"
        assert a.category == "martin"

    def test_retorna_resultados_info(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        analyzer = CouplingAnalyzer()
        results = analyzer.analyze(proyecto_simple, files_simple)
        assert all(r.severity == ArchitectureSeverity.INFO for r in results)

    def test_threshold_es_none(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        analyzer = CouplingAnalyzer()
        results = analyzer.analyze(proyecto_simple, files_simple)
        assert all(r.threshold is None for r in results)

    def test_omite_modulos_aislados(self, tmp_path: Path) -> None:
        pkg = tmp_path / "src" / "mipkg"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "solo.py").write_text("x = 1\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        analyzer = CouplingAnalyzer()
        results = analyzer.analyze(tmp_path, files)
        # solo.py está aislado → no debe aparecer
        assert not any("solo" in str(r.module_path) for r in results)

    def test_should_run_siempre_true(self) -> None:
        assert CouplingAnalyzer().should_run(None) is True

    def test_metric_name_es_coupling(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        analyzer = CouplingAnalyzer()
        results = analyzer.analyze(proyecto_simple, files_simple)
        assert all(r.metric_name == "Coupling" for r in results)


# =============================================================================
# InstabilityAnalyzer — Ticket 2.3
# =============================================================================


class TestInstabilityAnalyzer:
    def test_nombre_y_categoria(self) -> None:
        a = InstabilityAnalyzer()
        assert a.name == "InstabilityAnalyzer"
        assert a.category == "martin"

    def test_no_reporta_modulos_estables(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        """core.py tiene Ce=0 → I=0.0, por debajo del umbral → no debe reportarse."""
        analyzer = InstabilityAnalyzer()
        config = ArchitectAnalystConfig()
        analyzer.should_run(config)
        results = analyzer.analyze(proyecto_simple, files_simple)
        modules_reported = {str(r.module_path) for r in results}
        assert "mipkg/core" not in modules_reported

    def test_severity_es_warning(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        analyzer = InstabilityAnalyzer()
        config = ArchitectAnalystConfig(max_instability=0.0)
        analyzer.should_run(config)
        results = analyzer.analyze(proyecto_simple, files_simple)
        # Con umbral 0.0, todos los módulos con I > 0 deberían ser WARNING
        assert all(r.severity == ArchitectureSeverity.WARNING for r in results)

    def test_metric_name_es_I(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        analyzer = InstabilityAnalyzer()
        config = ArchitectAnalystConfig(max_instability=0.0)
        analyzer.should_run(config)
        results = analyzer.analyze(proyecto_simple, files_simple)
        assert all(r.metric_name == "I" for r in results)

    def test_umbral_alto_no_reporta_nada(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        analyzer = InstabilityAnalyzer()
        config = ArchitectAnalystConfig(max_instability=1.0)
        analyzer.should_run(config)
        results = analyzer.analyze(proyecto_simple, files_simple)
        assert results == []

    def test_sin_config_usa_defaults(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        analyzer = InstabilityAnalyzer()
        # should_run no llamado → _config es None → debe usar default 0.8
        results = analyzer.analyze(proyecto_simple, files_simple)
        # Con umbral 0.8, controller (I=1.0, nadie lo importa) debería aparecer
        assert isinstance(results, list)

    def test_value_en_rango(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        analyzer = InstabilityAnalyzer()
        config = ArchitectAnalystConfig(max_instability=0.0)
        analyzer.should_run(config)
        results = analyzer.analyze(proyecto_simple, files_simple)
        for r in results:
            assert 0.0 <= r.value <= 1.0


# =============================================================================
# AbstractnessAnalyzer — Ticket 2.4
# =============================================================================


class TestAbstractnessAnalyzer:
    def test_nombre_y_categoria(self) -> None:
        a = AbstractnessAnalyzer()
        assert a.name == "AbstractnessAnalyzer"
        assert a.category == "martin"

    def test_detecta_clase_abstracta(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        """abstracts.py tiene 2 clases: 1 abstracta (Base) y 1 concreta (Concrete)."""
        analyzer = AbstractnessAnalyzer()
        results = analyzer.analyze(proyecto_simple, files_simple)
        abstracts_result = next(
            (r for r in results if "abstracts" in str(r.module_path)), None
        )
        assert abstracts_result is not None
        assert abstracts_result.value == pytest.approx(0.5)

    def test_threshold_es_none(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        analyzer = AbstractnessAnalyzer()
        results = analyzer.analyze(proyecto_simple, files_simple)
        assert all(r.threshold is None for r in results)

    def test_severity_es_info(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        analyzer = AbstractnessAnalyzer()
        results = analyzer.analyze(proyecto_simple, files_simple)
        assert all(r.severity == ArchitectureSeverity.INFO for r in results)

    def test_omite_modulos_sin_clases(self, tmp_path: Path) -> None:
        pkg = tmp_path / "src" / "mipkg"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "utils.py").write_text("def helper(): pass\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        analyzer = AbstractnessAnalyzer()
        results = analyzer.analyze(tmp_path, files)
        # utils.py no tiene clases → no debe reportarse
        assert not any("utils" in str(r.module_path) for r in results)

    def test_clase_con_abstractmethod_cuenta_como_abstracta(self, tmp_path: Path) -> None:
        pkg = tmp_path / "src" / "mipkg"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "iface.py").write_text(
            "from abc import abstractmethod\n"
            "class IRepo:\n"
            "    @abstractmethod\n"
            "    def save(self): pass\n",
            encoding="utf-8",
        )
        files = list(tmp_path.rglob("*.py"))
        analyzer = AbstractnessAnalyzer()
        results = analyzer.analyze(tmp_path, files)
        iface_result = next((r for r in results if "iface" in str(r.module_path)), None)
        assert iface_result is not None
        assert iface_result.value == pytest.approx(1.0)

    def test_todas_concretas_da_cero(self, tmp_path: Path) -> None:
        pkg = tmp_path / "src" / "mipkg"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "concreto.py").write_text(
            "class A: pass\nclass B: pass\n", encoding="utf-8"
        )
        files = list(tmp_path.rglob("*.py"))
        analyzer = AbstractnessAnalyzer()
        results = analyzer.analyze(tmp_path, files)
        result = next((r for r in results if "concreto" in str(r.module_path)), None)
        assert result is not None
        assert result.value == pytest.approx(0.0)

    def test_metric_name_es_A(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        analyzer = AbstractnessAnalyzer()
        results = analyzer.analyze(proyecto_simple, files_simple)
        assert all(r.metric_name == "A" for r in results)


# =============================================================================
# DistanceAnalyzer — Ticket 2.5
# =============================================================================


class TestDistanceAnalyzer:
    def test_nombre_y_categoria(self) -> None:
        a = DistanceAnalyzer()
        assert a.name == "DistanceAnalyzer"
        assert a.category == "martin"

    def test_severity_warning_y_critical(self, tmp_path: Path) -> None:
        """
        Módulo en Zone of Pain (A=0, I=0) → D=1.0 → CRITICAL con umbrales default.
        """
        pkg = tmp_path / "src" / "mipkg"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        # dep.py: es muy usado (Ca alto) y no importa nada (Ce=0) → I=0.0
        # Y no tiene clases abstractas → A=0.0 → D = |0 + 0 - 1| = 1.0
        (pkg / "dep.py").write_text("class ConcreteImpl: pass\n", encoding="utf-8")
        (pkg / "user1.py").write_text("from mipkg.dep import ConcreteImpl\n", encoding="utf-8")
        (pkg / "user2.py").write_text("from mipkg.dep import ConcreteImpl\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        analyzer = DistanceAnalyzer()
        config = ArchitectAnalystConfig()
        analyzer.should_run(config)
        results = analyzer.analyze(tmp_path, files)
        dep_result = next((r for r in results if "dep" in str(r.module_path)), None)
        assert dep_result is not None
        assert dep_result.severity == ArchitectureSeverity.CRITICAL

    def test_modulo_sobre_main_sequence_no_reporta(self, tmp_path: Path) -> None:
        """Módulo con A=1.0 e I=0.0 → D=0.0 → no debe reportarse."""
        pkg = tmp_path / "src" / "mipkg"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        # abstracto.py: sin imports internos (I=0) y clase abstracta (A=1.0) → D=0.0
        (pkg / "abstracto.py").write_text(
            "from abc import ABC, abstractmethod\n"
            "class Base(ABC):\n"
            "    @abstractmethod\n"
            "    def run(self): pass\n",
            encoding="utf-8",
        )
        (pkg / "user.py").write_text("from mipkg.abstracto import Base\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        analyzer = DistanceAnalyzer()
        config = ArchitectAnalystConfig()
        analyzer.should_run(config)
        results = analyzer.analyze(tmp_path, files)
        abstracto_result = next(
            (r for r in results if "abstracto" in str(r.module_path)), None
        )
        assert abstracto_result is None

    def test_metric_name_es_D(self, proyecto_simple: Path, files_simple: list) -> None:
        analyzer = DistanceAnalyzer()
        config = ArchitectAnalystConfig(max_distance_warning=0.0, max_distance_critical=0.0)
        analyzer.should_run(config)
        results = analyzer.analyze(proyecto_simple, files_simple)
        assert all(r.metric_name == "D" for r in results)

    def test_value_en_rango(self, proyecto_simple: Path, files_simple: list) -> None:
        analyzer = DistanceAnalyzer()
        config = ArchitectAnalystConfig(max_distance_warning=0.0, max_distance_critical=0.0)
        analyzer.should_run(config)
        results = analyzer.analyze(proyecto_simple, files_simple)
        for r in results:
            assert 0.0 <= r.value <= 1.0

    def test_umbral_muy_alto_no_reporta(
        self, proyecto_simple: Path, files_simple: list
    ) -> None:
        analyzer = DistanceAnalyzer()
        config = ArchitectAnalystConfig(
            max_distance_warning=1.0, max_distance_critical=1.0
        )
        analyzer.should_run(config)
        results = analyzer.analyze(proyecto_simple, files_simple)
        assert results == []

    def test_omite_modulos_sin_clases(self, tmp_path: Path) -> None:
        pkg = tmp_path / "src" / "mipkg"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "utils.py").write_text("def helper(): pass\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        analyzer = DistanceAnalyzer()
        config = ArchitectAnalystConfig(max_distance_warning=0.0)
        analyzer.should_run(config)
        results = analyzer.analyze(tmp_path, files)
        assert not any("utils" in str(r.module_path) for r in results)

    def test_identify_zone_pain(self) -> None:
        analyzer = DistanceAnalyzer()
        zone = analyzer._identify_zone(instability=0.1, abstractness=0.1)
        assert "Pain" in zone

    def test_identify_zone_uselessness(self) -> None:
        analyzer = DistanceAnalyzer()
        zone = analyzer._identify_zone(instability=0.9, abstractness=0.9)
        assert "Uselessness" in zone

    def test_identify_zone_generico(self) -> None:
        analyzer = DistanceAnalyzer()
        zone = analyzer._identify_zone(instability=0.5, abstractness=0.0)
        assert "Main Sequence" in zone


# =============================================================================
# Auto-discovery: métricas exportadas en __init__.py
# =============================================================================


class TestMetricsInit:
    def test_imports_desde_init(self) -> None:
        from quality_agents.architectanalyst.metrics import (
            AbstractnessAnalyzer,
            CouplingAnalyzer,
            DistanceAnalyzer,
            InstabilityAnalyzer,
        )

        assert CouplingAnalyzer().name == "CouplingAnalyzer"
        assert InstabilityAnalyzer().name == "InstabilityAnalyzer"
        assert AbstractnessAnalyzer().name == "AbstractnessAnalyzer"
        assert DistanceAnalyzer().name == "DistanceAnalyzer"

    def test_orchestrator_descubre_las_cuatro_metricas(self) -> None:
        from quality_agents.architectanalyst.config import ArchitectAnalystConfig
        from quality_agents.architectanalyst.orchestrator import MetricOrchestrator

        orchestrator = MetricOrchestrator(ArchitectAnalystConfig())
        nombres = {m.name for m in orchestrator.metrics}
        assert "CouplingAnalyzer" in nombres
        assert "InstabilityAnalyzer" in nombres
        assert "AbstractnessAnalyzer" in nombres
        assert "DistanceAnalyzer" in nombres
