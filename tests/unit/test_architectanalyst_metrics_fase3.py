"""
Tests unitarios para ciclos y capas (Fase 3 de ArchitectAnalyst).

Cubre:
  - DependencyCyclesAnalyzer — Tarjan SCC (Ticket 3.1)
  - LayerViolationsAnalyzer — validación de capas (Ticket 3.2)

Ticket: 3.3
Fecha: 2026-03-01
"""

from pathlib import Path

import pytest

from quality_agents.architectanalyst.config import ArchitectAnalystConfig, LayersConfig
from quality_agents.architectanalyst.metrics.dependency_cycles_analyzer import (
    DependencyCyclesAnalyzer,
)
from quality_agents.architectanalyst.metrics.layer_violations_analyzer import (
    LayerViolationsAnalyzer,
)
from quality_agents.architectanalyst.models import ArchitectureSeverity


# =============================================================================
# Helpers para construir proyectos sintéticos
# =============================================================================


def _make_pkg(tmp_path: Path, name: str) -> Path:
    """Crea un paquete Python vacío en src/<name>/."""
    pkg = tmp_path / "src" / name
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    return pkg


# =============================================================================
# DependencyCyclesAnalyzer — Ticket 3.1
# =============================================================================


class TestDependencyCyclesAnalyzer:

    # --- Metadatos ---

    def test_nombre_y_categoria(self) -> None:
        a = DependencyCyclesAnalyzer()
        assert a.name == "DependencyCyclesAnalyzer"
        assert a.category == "cycles"

    def test_priority_es_uno(self) -> None:
        assert DependencyCyclesAnalyzer().priority == 1

    def test_should_run_siempre_true(self) -> None:
        assert DependencyCyclesAnalyzer().should_run(None) is True

    # --- Sin ciclos ---

    def test_sin_ciclos_retorna_lista_vacia(self, tmp_path: Path) -> None:
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "core.py").write_text("class Core: pass\n", encoding="utf-8")
        (pkg / "service.py").write_text(
            "from mipkg.core import Core\n", encoding="utf-8"
        )
        files = list(tmp_path.rglob("*.py"))
        analyzer = DependencyCyclesAnalyzer()
        results = analyzer.analyze(tmp_path, files)
        assert results == []

    def test_arbol_sin_ciclos_lineal(self, tmp_path: Path) -> None:
        """A → B → C sin ciclos."""
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "a.py").write_text("from mipkg.b import B\n", encoding="utf-8")
        (pkg / "b.py").write_text("from mipkg.c import C\n", encoding="utf-8")
        (pkg / "c.py").write_text("class C: pass\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        assert DependencyCyclesAnalyzer().analyze(tmp_path, files) == []

    # --- Ciclo directo (2 nodos) ---

    def test_detecta_ciclo_directo_dos_nodos(self, tmp_path: Path) -> None:
        """A importa B y B importa A → ciclo directo."""
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "a.py").write_text("from mipkg.b import B\n", encoding="utf-8")
        (pkg / "b.py").write_text("from mipkg.a import A\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        results = DependencyCyclesAnalyzer().analyze(tmp_path, files)
        assert len(results) == 1
        assert results[0].severity == ArchitectureSeverity.CRITICAL

    def test_ciclo_directo_threshold_cero(self, tmp_path: Path) -> None:
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "a.py").write_text("from mipkg.b import B\n", encoding="utf-8")
        (pkg / "b.py").write_text("from mipkg.a import A\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        results = DependencyCyclesAnalyzer().analyze(tmp_path, files)
        assert results[0].threshold == 0.0

    def test_ciclo_directo_metric_name(self, tmp_path: Path) -> None:
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "a.py").write_text("from mipkg.b import B\n", encoding="utf-8")
        (pkg / "b.py").write_text("from mipkg.a import A\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        results = DependencyCyclesAnalyzer().analyze(tmp_path, files)
        assert results[0].metric_name == "DependencyCycle"

    def test_ciclo_directo_value_es_tamaño_del_ciclo(self, tmp_path: Path) -> None:
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "a.py").write_text("from mipkg.b import B\n", encoding="utf-8")
        (pkg / "b.py").write_text("from mipkg.a import A\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        results = DependencyCyclesAnalyzer().analyze(tmp_path, files)
        assert results[0].value == 2.0

    # --- Ciclo largo (3+ nodos) ---

    def test_detecta_ciclo_tres_nodos(self, tmp_path: Path) -> None:
        """A→B→C→A."""
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "a.py").write_text("from mipkg.b import B\n", encoding="utf-8")
        (pkg / "b.py").write_text("from mipkg.c import C\n", encoding="utf-8")
        (pkg / "c.py").write_text("from mipkg.a import A\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        results = DependencyCyclesAnalyzer().analyze(tmp_path, files)
        assert len(results) == 1
        assert results[0].value == 3.0

    def test_ciclo_tres_nodos_mensaje_contiene_arrow(self, tmp_path: Path) -> None:
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "a.py").write_text("from mipkg.b import B\n", encoding="utf-8")
        (pkg / "b.py").write_text("from mipkg.c import C\n", encoding="utf-8")
        (pkg / "c.py").write_text("from mipkg.a import A\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        results = DependencyCyclesAnalyzer().analyze(tmp_path, files)
        assert "→" in results[0].message

    # --- Dos ciclos independientes ---

    def test_detecta_dos_ciclos_independientes(self, tmp_path: Path) -> None:
        """Ciclo 1: A↔B  |  Ciclo 2: C↔D."""
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "a.py").write_text("from mipkg.b import B\n", encoding="utf-8")
        (pkg / "b.py").write_text("from mipkg.a import A\n", encoding="utf-8")
        (pkg / "c.py").write_text("from mipkg.d import D\n", encoding="utf-8")
        (pkg / "d.py").write_text("from mipkg.c import C\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        results = DependencyCyclesAnalyzer().analyze(tmp_path, files)
        assert len(results) == 2

    # --- Proyecto vacío ---

    def test_sin_archivos_retorna_lista_vacia(self, tmp_path: Path) -> None:
        results = DependencyCyclesAnalyzer().analyze(tmp_path, [])
        assert results == []

    # --- Auto-discovery ---

    def test_orchestrator_descubre_dependency_cycles(self) -> None:
        from quality_agents.architectanalyst.orchestrator import MetricOrchestrator

        orchestrator = MetricOrchestrator(ArchitectAnalystConfig())
        nombres = {m.name for m in orchestrator.metrics}
        assert "DependencyCyclesAnalyzer" in nombres


# =============================================================================
# LayerViolationsAnalyzer — Ticket 3.2
# =============================================================================


def _config_con_capas(**layers: list) -> ArchitectAnalystConfig:
    """Crea ArchitectAnalystConfig con LayersConfig a partir de kwargs."""
    config = ArchitectAnalystConfig()
    config.layers = LayersConfig(rules=dict(layers))
    return config


class TestLayerViolationsAnalyzer:

    # --- Metadatos ---

    def test_nombre_y_categoria(self) -> None:
        a = LayerViolationsAnalyzer()
        assert a.name == "LayerViolationsAnalyzer"
        assert a.category == "cycles"

    def test_priority_es_dos(self) -> None:
        assert LayerViolationsAnalyzer().priority == 2

    # --- should_run ---

    def test_should_run_false_sin_config(self) -> None:
        a = LayerViolationsAnalyzer()
        assert a.should_run(None) is False

    def test_should_run_false_sin_reglas(self) -> None:
        a = LayerViolationsAnalyzer()
        config = ArchitectAnalystConfig()  # LayersConfig vacío por defecto
        assert a.should_run(config) is False

    def test_should_run_true_con_reglas(self) -> None:
        a = LayerViolationsAnalyzer()
        config = _config_con_capas(domain=[], application=["domain"])
        assert a.should_run(config) is True

    # --- Sin violaciones ---

    def test_sin_violaciones_cuando_deps_son_correctas(self, tmp_path: Path) -> None:
        """application puede importar domain → OK."""
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "domain").mkdir()
        (pkg / "domain" / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "domain" / "entity.py").write_text(
            "class Entity: pass\n", encoding="utf-8"
        )
        (pkg / "application").mkdir()
        (pkg / "application" / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "application" / "service.py").write_text(
            "from mipkg.domain.entity import Entity\n", encoding="utf-8"
        )
        files = list(tmp_path.rglob("*.py"))
        config = _config_con_capas(domain=[], application=["domain"])
        analyzer = LayerViolationsAnalyzer()
        analyzer.should_run(config)
        results = analyzer.analyze(tmp_path, files)
        assert results == []

    def test_sin_violaciones_misma_capa(self, tmp_path: Path) -> None:
        """Imports dentro de la misma capa son siempre permitidos."""
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "domain").mkdir()
        (pkg / "domain" / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "domain" / "a.py").write_text("class A: pass\n", encoding="utf-8")
        (pkg / "domain" / "b.py").write_text(
            "from mipkg.domain.a import A\n", encoding="utf-8"
        )
        files = list(tmp_path.rglob("*.py"))
        config = _config_con_capas(domain=[], application=["domain"])
        analyzer = LayerViolationsAnalyzer()
        analyzer.should_run(config)
        results = analyzer.analyze(tmp_path, files)
        assert results == []

    # --- Con violaciones ---

    def test_detecta_violacion_domain_importa_application(
        self, tmp_path: Path
    ) -> None:
        """domain NO puede importar application → CRITICAL."""
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "domain").mkdir()
        (pkg / "domain" / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "domain" / "bad.py").write_text(
            "from mipkg.application.service import Service\n", encoding="utf-8"
        )
        (pkg / "application").mkdir()
        (pkg / "application" / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "application" / "service.py").write_text(
            "class Service: pass\n", encoding="utf-8"
        )
        files = list(tmp_path.rglob("*.py"))
        config = _config_con_capas(domain=[], application=["domain"])
        analyzer = LayerViolationsAnalyzer()
        analyzer.should_run(config)
        results = analyzer.analyze(tmp_path, files)
        assert len(results) == 1
        assert results[0].severity == ArchitectureSeverity.CRITICAL

    def test_violacion_threshold_cero(self, tmp_path: Path) -> None:
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "domain").mkdir()
        (pkg / "domain" / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "domain" / "bad.py").write_text(
            "from mipkg.application.svc import S\n", encoding="utf-8"
        )
        (pkg / "application").mkdir()
        (pkg / "application" / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "application" / "svc.py").write_text("class S: pass\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        config = _config_con_capas(domain=[], application=["domain"])
        analyzer = LayerViolationsAnalyzer()
        analyzer.should_run(config)
        results = analyzer.analyze(tmp_path, files)
        assert results[0].threshold == 0.0

    def test_violacion_metric_name(self, tmp_path: Path) -> None:
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "domain").mkdir()
        (pkg / "domain" / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "domain" / "bad.py").write_text(
            "from mipkg.application.svc import S\n", encoding="utf-8"
        )
        (pkg / "application").mkdir()
        (pkg / "application" / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "application" / "svc.py").write_text("class S: pass\n", encoding="utf-8")
        files = list(tmp_path.rglob("*.py"))
        config = _config_con_capas(domain=[], application=["domain"])
        analyzer = LayerViolationsAnalyzer()
        analyzer.should_run(config)
        results = analyzer.analyze(tmp_path, files)
        assert results[0].metric_name == "LayerViolation"

    def test_modulo_sin_capa_conocida_se_ignora(self, tmp_path: Path) -> None:
        """Módulos que no pertenecen a ninguna capa declarada no generan errores."""
        pkg = _make_pkg(tmp_path, "mipkg")
        (pkg / "utils.py").write_text("class Helper: pass\n", encoding="utf-8")
        (pkg / "domain").mkdir()
        (pkg / "domain" / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "domain" / "entity.py").write_text(
            "from mipkg.utils import Helper\n", encoding="utf-8"
        )
        files = list(tmp_path.rglob("*.py"))
        config = _config_con_capas(domain=[], application=["domain"])
        analyzer = LayerViolationsAnalyzer()
        analyzer.should_run(config)
        results = analyzer.analyze(tmp_path, files)
        # utils no pertenece a ninguna capa → no hay violación
        assert results == []

    # --- _find_layer ---

    def test_find_layer_detecta_capa_en_segmento(self) -> None:
        a = LayerViolationsAnalyzer()
        rules = {"domain": [], "application": ["domain"]}
        assert a._find_layer("mipkg.domain.entity", rules) == "domain"
        assert a._find_layer("mipkg.application.service", rules) == "application"

    def test_find_layer_retorna_none_si_no_hay_match(self) -> None:
        a = LayerViolationsAnalyzer()
        rules = {"domain": [], "application": ["domain"]}
        assert a._find_layer("mipkg.utils.helper", rules) is None

    def test_find_layer_toma_primer_segmento_que_coincide(self) -> None:
        """Si hay ambigüedad, toma el primer segmento (más cercano a la raíz)."""
        a = LayerViolationsAnalyzer()
        rules = {"domain": [], "application": ["domain"]}
        # "domain" aparece antes que "application" → retorna "domain"
        result = a._find_layer("mipkg.domain.application.entity", rules)
        assert result == "domain"

    # --- Auto-discovery (con config sin capas → no aparece) ---

    def test_orchestrator_no_ejecuta_sin_capas(self, tmp_path: Path) -> None:
        """LayerViolationsAnalyzer existe pero should_run=False sin reglas."""
        from quality_agents.architectanalyst.orchestrator import MetricOrchestrator

        config = ArchitectAnalystConfig()  # sin capas
        orchestrator = MetricOrchestrator(config)
        # La métrica existe en el orchestrator
        layer_metric = next(
            (m for m in orchestrator.metrics if m.name == "LayerViolationsAnalyzer"), None
        )
        assert layer_metric is not None
        # Pero should_run retorna False
        assert layer_metric.should_run(config) is False

    def test_orchestrator_descubre_layer_violations(self) -> None:
        from quality_agents.architectanalyst.orchestrator import MetricOrchestrator

        orchestrator = MetricOrchestrator(ArchitectAnalystConfig())
        nombres = {m.name for m in orchestrator.metrics}
        assert "LayerViolationsAnalyzer" in nombres
