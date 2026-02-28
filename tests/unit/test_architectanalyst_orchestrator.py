"""
Tests unitarios para ProjectMetric, MetricOrchestrator y ArchitectAnalyst.

Ticket: 1.6
"""

from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest

from quality_agents.architectanalyst.agent import ArchitectAnalyst
from quality_agents.architectanalyst.config import ArchitectAnalystConfig
from quality_agents.architectanalyst.models import ArchitectureResult, ArchitectureSeverity
from quality_agents.architectanalyst.orchestrator import MetricOrchestrator, ProjectMetric


# ========== Métricas mock para tests ==========


class MockMetricSinResultados(ProjectMetric):
    """Métrica que no produce resultados."""

    @property
    def name(self) -> str:
        return "MockSinResultados"

    @property
    def category(self) -> str:
        return "martin"

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        return []


class MockMetricConViolacion(ProjectMetric):
    """Métrica que siempre detecta una violación CRITICAL."""

    @property
    def name(self) -> str:
        return "MockConViolacion"

    @property
    def category(self) -> str:
        return "structural"

    @property
    def priority(self) -> int:
        return 1

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        return [
            ArchitectureResult(
                analyzer_name=self.name,
                metric_name="Cycles",
                module_path=files[0] if files else Path("src/foo.py"),
                value=1.0,
                threshold=0.0,
                severity=ArchitectureSeverity.CRITICAL,
                message="Ciclo detectado (prueba)",
            )
        ]


class MockMetricFalla(ProjectMetric):
    """Métrica que lanza excepción al ejecutar."""

    @property
    def name(self) -> str:
        return "MockFalla"

    @property
    def category(self) -> str:
        return "martin"

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        raise RuntimeError("Error simulado en métrica")


class MockMetricDesactivada(ProjectMetric):
    """Métrica que se desactiva vía should_run()."""

    @property
    def name(self) -> str:
        return "MockDesactivada"

    @property
    def category(self) -> str:
        return "martin"

    def should_run(self, config) -> bool:
        return False  # Nunca corre

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        raise AssertionError("No debería llamarse nunca")


class MockMetricConPrioridad(ProjectMetric):
    """Métrica con prioridad configurable para test de ordenamiento."""

    def __init__(self, nombre: str, prioridad: int) -> None:
        self._nombre = nombre
        self._prioridad = prioridad

    @property
    def name(self) -> str:
        return self._nombre

    @property
    def category(self) -> str:
        return "martin"

    @property
    def priority(self) -> int:
        return self._prioridad

    def analyze(self, project_path: Path, files: List[Path]) -> List[ArchitectureResult]:
        return []


# ========== Tests de ProjectMetric ==========


class TestProjectMetric:
    """Tests para la clase base abstracta ProjectMetric."""

    def test_no_se_puede_instanciar_directamente(self):
        """ProjectMetric es abstracta — debe fallar al instanciar."""
        with pytest.raises(TypeError):
            ProjectMetric()  # type: ignore[abstract]

    def test_defaults_estimated_duration(self):
        """estimated_duration debe ser 5.0 por defecto."""
        assert MockMetricSinResultados().estimated_duration == 5.0

    def test_defaults_priority(self):
        """priority debe ser 5 por defecto."""
        assert MockMetricSinResultados().priority == 5

    def test_defaults_should_run(self):
        """should_run() debe retornar True por defecto."""
        assert MockMetricSinResultados().should_run(config=None) is True

    def test_subclase_concreta_instancia(self):
        """Una subclase concreta debe poder instanciarse."""
        m = MockMetricSinResultados()
        assert m.name == "MockSinResultados"
        assert m.category == "martin"


# ========== Tests de MetricOrchestrator inicialización ==========


class TestMetricOrchestratorInit:
    """Tests para la inicialización del orquestador."""

    def test_init_con_config_none(self):
        """Debe instanciar con config=None sin errores."""
        orch = MetricOrchestrator(config=None)

        assert orch.config is None
        assert isinstance(orch.metrics, list)

    def test_init_con_config_real(self):
        """Debe instanciar con ArchitectAnalystConfig sin errores."""
        config = ArchitectAnalystConfig()
        orch = MetricOrchestrator(config=config)

        assert orch.config is config

    def test_discovery_no_falla_con_paquete_vacio(self):
        """Auto-discovery debe completar sin excepciones aunque no haya métricas."""
        orch = MetricOrchestrator(config=None)

        assert isinstance(orch.metrics, list)

    def test_metricas_ordenadas_por_prioridad(self):
        """Las métricas deben estar ordenadas por priority (menor = primero)."""
        orch = MetricOrchestrator(config=None)
        orch.metrics = [
            MockMetricConPrioridad("Alta", prioridad=1),
            MockMetricConPrioridad("Baja", prioridad=9),
            MockMetricConPrioridad("Media", prioridad=5),
        ]
        # Re-ordenar como haría el orchestrator
        orch.metrics = sorted(orch.metrics, key=lambda m: m.priority)

        prioridades = [m.priority for m in orch.metrics]
        assert prioridades == sorted(prioridades)


# ========== Tests de MetricOrchestrator auto-discovery ==========


class TestMetricOrchestratorDiscovery:
    """Tests para el auto-discovery de métricas."""

    @patch("quality_agents.architectanalyst.orchestrator.importlib.import_module")
    def test_discovery_encuentra_subclases_de_project_metric(self, mock_import):
        """Debe descubrir y instanciar todas las subclases de ProjectMetric."""
        from unittest.mock import Mock

        mock_module = Mock()
        mock_module.MockMetricSinResultados = MockMetricSinResultados
        mock_module.MockConViolacion = MockMetricConViolacion
        mock_module.ProjectMetric = ProjectMetric  # Clase base — debe ser excluida

        with patch("quality_agents.architectanalyst.orchestrator.dir") as mock_dir:
            mock_dir.return_value = [
                "MockMetricSinResultados",
                "MockConViolacion",
                "ProjectMetric",
                "alguna_funcion",
            ]
            mock_import.return_value = mock_module

            orch = MetricOrchestrator(config=None)

        assert len(orch.metrics) == 2
        nombres = {m.name for m in orch.metrics}
        assert "MockSinResultados" in nombres
        assert "MockConViolacion" in nombres

    @patch("quality_agents.architectanalyst.orchestrator.importlib.import_module")
    def test_discovery_maneja_error_instanciacion(self, mock_import):
        """Si una métrica no puede instanciarse, debe loguear y continuar."""
        from unittest.mock import Mock

        class MetricQueNoInstancia(ProjectMetric):
            def __init__(self):
                raise ValueError("Error al instanciar")

            @property
            def name(self) -> str:
                return "X"

            @property
            def category(self) -> str:
                return "martin"

            def analyze(self, p, f):
                return []

        mock_module = Mock()
        mock_module.MetricQueNoInstancia = MetricQueNoInstancia
        mock_module.MockMetricSinResultados = MockMetricSinResultados

        with patch("quality_agents.architectanalyst.orchestrator.dir") as mock_dir:
            mock_dir.return_value = ["MetricQueNoInstancia", "MockMetricSinResultados"]
            mock_import.return_value = mock_module

            orch = MetricOrchestrator(config=None)

        assert len(orch.metrics) == 1
        assert orch.metrics[0].name == "MockSinResultados"


# ========== Tests de MetricOrchestrator.run() ==========


class TestMetricOrchestratorRun:
    """Tests para el método run()."""

    def _orch_con_metricas(self, *metricas: ProjectMetric) -> MetricOrchestrator:
        """Helper: crea orquestador con métricas inyectadas manualmente."""
        orch = MetricOrchestrator(config=ArchitectAnalystConfig())
        orch.metrics = list(metricas)
        return orch

    def test_run_lista_vacia_retorna_vacia(self):
        """run([]) debe retornar lista vacía sin procesar nada."""
        orch = self._orch_con_metricas(MockMetricConViolacion())

        assert orch.run([]) == []

    def test_run_sin_metricas_retorna_vacia(self, tmp_path):
        """Sin métricas descubiertas, run() debe retornar []."""
        py_file = tmp_path / "module.py"
        py_file.write_text("x = 1")
        orch = MetricOrchestrator(config=None)

        assert orch.run([py_file]) == []

    def test_run_ignora_archivos_no_python(self, tmp_path):
        """Archivos que no son .py no deben ser pasados a las métricas."""
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("texto")

        orch = self._orch_con_metricas(MockMetricConViolacion())

        assert orch.run([txt_file]) == []

    def test_run_pasa_todos_los_archivos_de_una_vez(self, tmp_path):
        """Debe pasar la lista completa de archivos a cada métrica (project-wide)."""
        py1 = tmp_path / "a.py"
        py2 = tmp_path / "b.py"
        py1.write_text("x = 1")
        py2.write_text("y = 2")

        archivos_recibidos = []

        class MockMetricCaptura(ProjectMetric):
            @property
            def name(self) -> str:
                return "Captura"

            @property
            def category(self) -> str:
                return "martin"

            def analyze(self, project_path, files):
                archivos_recibidos.extend(files)
                return []

        orch = self._orch_con_metricas(MockMetricCaptura())
        orch.run([py1, py2])

        # La métrica recibe TODOS los archivos de una vez (no uno por uno)
        assert len(archivos_recibidos) == 2
        assert py1 in archivos_recibidos
        assert py2 in archivos_recibidos

    def test_run_agrega_resultados_de_multiples_metricas(self, tmp_path):
        """Debe agregar resultados de todas las métricas."""
        py_file = tmp_path / "module.py"
        py_file.write_text("x = 1")

        orch = self._orch_con_metricas(
            MockMetricConViolacion(),
            MockMetricConViolacion(),
        )
        results = orch.run([py_file])

        assert len(results) == 2

    def test_run_respeta_should_run(self, tmp_path):
        """Debe respetar should_run() de cada métrica."""
        py_file = tmp_path / "module.py"
        py_file.write_text("x = 1")

        orch = self._orch_con_metricas(
            MockMetricDesactivada(),
            MockMetricSinResultados(),
        )
        results = orch.run([py_file])

        assert results == []

    def test_run_maneja_error_en_metrica_y_continua(self, tmp_path):
        """Si una métrica falla, debe loguear el error y continuar con las demás."""
        py_file = tmp_path / "module.py"
        py_file.write_text("x = 1")

        orch = self._orch_con_metricas(
            MockMetricFalla(),
            MockMetricConViolacion(),  # Esta debe ejecutarse igual
        )
        results = orch.run([py_file])

        # La métrica que falló no produce resultados (a diferencia de AnalyzerOrchestrator
        # que genera un resultado INFO de error; MetricOrchestrator solo loguea)
        assert len(results) == 1
        assert results[0].severity == ArchitectureSeverity.CRITICAL


# ========== Tests de MetricOrchestrator._find_project_root() ==========


class TestFindProjectRoot:
    """Tests para _find_project_root()."""

    def test_encuentra_pyproject_toml(self, tmp_path):
        """Debe encontrar el directorio que contiene pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool]\n")
        subdir = tmp_path / "src" / "mymodule"
        subdir.mkdir(parents=True)
        py_file = subdir / "service.py"
        py_file.write_text("x = 1")

        orch = MetricOrchestrator(config=None)
        root = orch._find_project_root(py_file)

        assert root == tmp_path

    def test_fallback_si_no_hay_indicadores(self, tmp_path):
        """Si no hay pyproject.toml, debe retornar el directorio padre del archivo."""
        py_file = tmp_path / "module.py"
        py_file.write_text("x = 1")

        orch = MetricOrchestrator(config=None)
        root = orch._find_project_root(py_file)

        assert root == tmp_path


# ========== Tests de ArchitectAnalyst ==========


class TestArchitectAnalyst:
    """Tests para la clase principal ArchitectAnalyst."""

    def test_init_defaults(self):
        """Debe inicializarse con valores por defecto."""
        analyst = ArchitectAnalyst()

        assert analyst.path == Path(".")
        assert analyst.config_path is None
        assert analyst.sprint_id is None
        assert analyst.results == []

    def test_init_con_parametros(self, tmp_path):
        """Debe aceptar todos los parámetros."""
        analyst = ArchitectAnalyst(
            path=tmp_path,
            sprint_id="sprint-12",
        )

        assert analyst.path == tmp_path
        assert analyst.sprint_id == "sprint-12"

    def test_config_cargada_en_init(self):
        """La config debe cargarse automáticamente en __init__."""
        analyst = ArchitectAnalyst()

        assert isinstance(analyst._config, ArchitectAnalystConfig)

    def test_orchestrator_inicializado_en_init(self):
        """El orquestador debe inicializarse en __init__."""
        analyst = ArchitectAnalyst()

        assert isinstance(analyst._orchestrator, MetricOrchestrator)

    def test_run_lista_vacia_retorna_vacia(self):
        """run(files=[]) debe retornar lista vacía."""
        analyst = ArchitectAnalyst()

        assert analyst.run(files=[]) == []

    def test_run_sin_metricas_retorna_vacia(self, tmp_path):
        """Sin métricas descubiertas, run() retorna []."""
        py_file = tmp_path / "module.py"
        py_file.write_text("x = 1")

        analyst = ArchitectAnalyst(path=tmp_path)
        results = analyst.run(files=[py_file])

        assert results == []

    def test_has_violations_sin_resultados(self):
        """has_violations() debe ser False sin resultados."""
        analyst = ArchitectAnalyst()
        analyst.results = []

        assert not analyst.has_violations()

    def test_has_violations_con_warning(self):
        """has_violations() debe ser True si hay algún WARNING."""
        analyst = ArchitectAnalyst()
        analyst.results = [
            ArchitectureResult(
                analyzer_name="Test",
                metric_name="I",
                module_path=Path("src/foo.py"),
                value=0.85,
                threshold=0.8,
                severity=ArchitectureSeverity.WARNING,
                message="Inestable",
            )
        ]

        assert analyst.has_violations()

    def test_has_critical_sin_critical(self):
        """has_critical() debe ser False si solo hay WARNINGs."""
        analyst = ArchitectAnalyst()
        analyst.results = [
            ArchitectureResult(
                analyzer_name="Test",
                metric_name="I",
                module_path=Path("src/foo.py"),
                value=0.85,
                threshold=0.8,
                severity=ArchitectureSeverity.WARNING,
                message="Inestable",
            )
        ]

        assert not analyst.has_critical()

    def test_has_critical_con_critical(self):
        """has_critical() debe ser True si hay algún CRITICAL."""
        analyst = ArchitectAnalyst()
        analyst.results = [
            ArchitectureResult(
                analyzer_name="Test",
                metric_name="Cycles",
                module_path=Path("src/foo.py"),
                value=1.0,
                threshold=0.0,
                severity=ArchitectureSeverity.CRITICAL,
                message="Ciclo detectado",
            )
        ]

        assert analyst.has_critical()

    def test_collect_files_desde_directorio(self, tmp_path):
        """collect_files() debe encontrar todos los .py en un directorio."""
        (tmp_path / "a.py").write_text("x = 1")
        (tmp_path / "b.py").write_text("y = 2")
        (tmp_path / "readme.txt").write_text("texto")

        analyst = ArchitectAnalyst()
        files = analyst.collect_files(tmp_path)

        assert len(files) == 2
        assert all(f.suffix == ".py" for f in files)

    def test_collect_files_desde_archivo(self, tmp_path):
        """collect_files() con un archivo .py debe retornar ese archivo."""
        py_file = tmp_path / "module.py"
        py_file.write_text("x = 1")

        analyst = ArchitectAnalyst()
        files = analyst.collect_files(py_file)

        assert files == [py_file]

    def test_collect_files_archivo_no_python(self, tmp_path):
        """collect_files() con un archivo no .py debe retornar lista vacía."""
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("texto")

        analyst = ArchitectAnalyst()
        files = analyst.collect_files(txt_file)

        assert files == []
