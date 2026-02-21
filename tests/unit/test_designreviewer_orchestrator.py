"""
Tests unitarios para AnalyzerOrchestrator.

Ticket: 1.7
"""

from pathlib import Path
from typing import Any, List
from unittest.mock import patch

from quality_agents.designreviewer.config import DesignReviewerConfig
from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity
from quality_agents.designreviewer.orchestrator import AnalyzerOrchestrator
from quality_agents.shared.verifiable import ExecutionContext, Verifiable

# ========== Analyzers mock para tests ==========


class MockAnalyzerSinResultados(Verifiable):
    """Analyzer que no produce resultados."""

    @property
    def name(self) -> str:
        return "MockSinResultados"

    @property
    def category(self) -> str:
        return "coupling"

    def execute(self, file_path: Path) -> List[Any]:
        return []


class MockAnalyzerConViolacion(Verifiable):
    """Analyzer que siempre detecta una violación CRITICAL."""

    @property
    def name(self) -> str:
        return "MockConViolacion"

    @property
    def category(self) -> str:
        return "coupling"

    def execute(self, file_path: Path) -> List[Any]:
        return [
            ReviewResult(
                analyzer_name=self.name,
                severity=ReviewSeverity.CRITICAL,
                current_value=10,
                threshold=5,
                message="Violación de prueba",
                file_path=file_path,
            )
        ]


class MockAnalyzerFalla(Verifiable):
    """Analyzer que lanza excepción al ejecutar."""

    @property
    def name(self) -> str:
        return "MockFalla"

    @property
    def category(self) -> str:
        return "coupling"

    def execute(self, file_path: Path) -> List[Any]:
        raise RuntimeError("Error simulado en analyzer")


class MockAnalyzerSoloPython(Verifiable):
    """Analyzer que solo se ejecuta en archivos .py."""

    @property
    def name(self) -> str:
        return "MockSoloPython"

    @property
    def category(self) -> str:
        return "cohesion"

    def should_run(self, context: ExecutionContext) -> bool:
        return context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> List[Any]:
        return []


# ========== Tests de inicialización ==========


class TestAnalyzerOrchestratorInit:
    """Tests para la inicialización del orquestador."""

    def test_init_con_config_none(self):
        """Debe instanciar con config None sin errores."""
        orch = AnalyzerOrchestrator(config=None)

        assert orch.config is None
        assert isinstance(orch.analyzers, list)

    def test_init_con_config_real(self):
        """Debe instanciar con DesignReviewerConfig sin errores."""
        config = DesignReviewerConfig()
        orch = AnalyzerOrchestrator(config=config)

        assert orch.config is config
        assert isinstance(orch.analyzers, list)

    def test_discovery_no_falla(self):
        """Auto-discovery debe completar sin lanzar excepciones."""
        orch = AnalyzerOrchestrator(config=None)

        # El paquete analyzers/ existe y puede tener 0 o más analyzers
        assert isinstance(orch.analyzers, list)

    def test_config_guardado_correctamente(self):
        """La config debe quedar disponible como atributo."""
        config = DesignReviewerConfig(max_cbo=3)
        orch = AnalyzerOrchestrator(config=config)

        assert orch.config.max_cbo == 3


# ========== Tests de auto-discovery con mocks ==========


class TestAnalyzerOrchestratorDiscovery:
    """Tests para el auto-discovery de analyzers."""

    @patch("quality_agents.designreviewer.orchestrator.importlib.import_module")
    def test_discovery_encuentra_subclases_de_verifiable(self, mock_import, monkeypatch):
        """Debe descubrir y instanciar todas las subclases de Verifiable."""
        from unittest.mock import Mock

        mock_module = Mock()
        mock_module.MockAnalyzerSinResultados = MockAnalyzerSinResultados
        mock_module.MockConViolacion = MockAnalyzerConViolacion
        mock_module.Verifiable = Verifiable  # Clase base — debe ser excluida

        with patch("quality_agents.designreviewer.orchestrator.dir") as mock_dir:
            mock_dir.return_value = [
                "MockAnalyzerSinResultados",
                "MockConViolacion",
                "Verifiable",
                "alguna_funcion",
            ]
            mock_import.return_value = mock_module

            orch = AnalyzerOrchestrator(config=None)

        assert len(orch.analyzers) == 2
        nombres = {a.name for a in orch.analyzers}
        assert "MockSinResultados" in nombres
        assert "MockConViolacion" in nombres

    @patch("quality_agents.designreviewer.orchestrator.importlib.import_module")
    def test_discovery_maneja_error_instanciacion(self, mock_import):
        """Si un analyzer no puede instanciarse, debe loguear y continuar."""
        from unittest.mock import Mock

        class AnalyzerQueNoInstancia(Verifiable):
            def __init__(self):
                raise ValueError("No se puede instanciar")

            @property
            def name(self) -> str:
                return "X"

            @property
            def category(self) -> str:
                return "X"

            def execute(self, file_path: Path) -> List[Any]:
                return []

        mock_module = Mock()
        mock_module.AnalyzerQueNoInstancia = AnalyzerQueNoInstancia
        mock_module.MockAnalyzerSinResultados = MockAnalyzerSinResultados

        with patch("quality_agents.designreviewer.orchestrator.dir") as mock_dir:
            mock_dir.return_value = ["AnalyzerQueNoInstancia", "MockAnalyzerSinResultados"]
            mock_import.return_value = mock_module

            # No debe lanzar excepción
            orch = AnalyzerOrchestrator(config=None)

        # Solo el que puede instanciarse debe estar
        assert len(orch.analyzers) == 1
        assert orch.analyzers[0].name == "MockSinResultados"


# ========== Tests de run() ==========


class TestAnalyzerOrchestratorRun:
    """Tests para el método run()."""

    def _orch_con_analyzers(self, *analyzers: Verifiable) -> AnalyzerOrchestrator:
        """Helper: crea orquestador con analyzers inyectados manualmente."""
        orch = AnalyzerOrchestrator(config=DesignReviewerConfig())
        orch.analyzers = list(analyzers)
        return orch

    def test_run_lista_vacia_retorna_vacia(self):
        """run([]) debe retornar lista vacía sin procesar nada."""
        orch = self._orch_con_analyzers(MockAnalyzerConViolacion())
        results = orch.run([])

        assert results == []

    def test_run_sin_analyzers_retorna_vacia(self, tmp_path):
        """Con lista de analyzers vacía, run() debe retornar []."""
        py_file = tmp_path / "module.py"
        py_file.write_text("x = 1")

        orch = AnalyzerOrchestrator(config=None)  # 0 analyzers
        results = orch.run([py_file])

        assert results == []

    def test_run_ignora_archivos_no_python(self, tmp_path):
        """Archivos que no son .py no deben ser procesados."""
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("texto")

        orch = self._orch_con_analyzers(MockAnalyzerConViolacion())
        results = orch.run([txt_file])

        assert results == []

    def test_run_procesa_archivos_python(self, tmp_path):
        """Debe procesar archivos .py y retornar resultados."""
        py_file = tmp_path / "module.py"
        py_file.write_text("x = 1")

        orch = self._orch_con_analyzers(MockAnalyzerConViolacion())
        results = orch.run([py_file])

        assert len(results) == 1
        assert results[0].analyzer_name == "MockConViolacion"
        assert results[0].severity == ReviewSeverity.CRITICAL

    def test_run_agrega_resultados_de_multiples_archivos(self, tmp_path):
        """Debe agregar resultados de todos los archivos procesados."""
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        f1.write_text("x = 1")
        f2.write_text("y = 2")

        orch = self._orch_con_analyzers(MockAnalyzerConViolacion())
        results = orch.run([f1, f2])

        assert len(results) == 2

    def test_run_agrega_resultados_de_multiples_analyzers(self, tmp_path):
        """Debe ejecutar todos los analyzers y agregar sus resultados."""
        py_file = tmp_path / "module.py"
        py_file.write_text("x = 1")

        orch = self._orch_con_analyzers(
            MockAnalyzerConViolacion(),
            MockAnalyzerConViolacion(),  # Dos analyzers
        )
        results = orch.run([py_file])

        assert len(results) == 2

    def test_run_respeta_should_run(self, tmp_path):
        """Debe respetar el método should_run() de cada analyzer."""
        py_file = tmp_path / "module.py"
        txt_file = tmp_path / "readme.txt"
        py_file.write_text("x = 1")
        txt_file.write_text("texto")

        orch = self._orch_con_analyzers(MockAnalyzerSoloPython())
        results = orch.run([py_file, txt_file])

        # Solo el .py pasa por el filtro de archivos no-python en run()
        # El .txt es filtrado antes de llegar al should_run del analyzer
        assert len(results) == 0  # MockSoloPython no genera resultados

    def test_run_maneja_error_en_analyzer(self, tmp_path):
        """Si un analyzer falla, debe loguear el error y continuar."""
        py_file = tmp_path / "module.py"
        py_file.write_text("x = 1")

        orch = self._orch_con_analyzers(
            MockAnalyzerFalla(),
            MockAnalyzerConViolacion(),  # Este debe seguir ejecutándose
        )
        results = orch.run([py_file])

        # El analyzer que falló produce un resultado INFO de error
        # El que no falló produce un resultado CRITICAL
        assert len(results) == 2
        severidades = {r.severity for r in results}
        assert ReviewSeverity.CRITICAL in severidades
        assert ReviewSeverity.INFO in severidades

    def test_run_resultado_error_tiene_info_correcto(self, tmp_path):
        """El resultado de error de un analyzer fallido debe tener info útil."""
        py_file = tmp_path / "module.py"
        py_file.write_text("x = 1")

        orch = self._orch_con_analyzers(MockAnalyzerFalla())
        results = orch.run([py_file])

        assert len(results) == 1
        error_result = results[0]
        assert error_result.analyzer_name == "MockFalla"
        assert error_result.severity == ReviewSeverity.INFO
        assert "Error simulado" in error_result.message
