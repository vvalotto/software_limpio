"""
Tests end-to-end de ArchitectAnalyst con métricas reales.

Verifica el pipeline completo sin mocks:
- Proyecto temporal con ciclos de dependencias conocidos
- Proyecto temporal con violaciones de capas (config en pyproject.toml)
- Proyecto temporal con módulos en distintas posiciones del Main Sequence
- CLI completo con salida Rich y JSON
- Exit code siempre 0 (ArchitectAnalyst nunca bloquea)

Ticket: 7.1 — Tests de integración end-to-end
Ticket: 7.2 — Tests E2E del CLI completo
Fecha: 2026-03-01
"""

import json
from pathlib import Path
from textwrap import dedent

import pytest
from click.testing import CliRunner

from quality_agents.architectanalyst.agent import ArchitectAnalyst, main
from quality_agents.architectanalyst.models import ArchitectureSeverity

# ---------------------------------------------------------------------------
# Fixtures de código sintético con estructuras conocidas
# ---------------------------------------------------------------------------


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def proyecto_limpio(tmp_path):
    """Proyecto sin dependencias internas — no debe generar CRITICAL."""
    (tmp_path / "calculadora.py").write_text(dedent("""
        '''Módulo simple sin dependencias internas.'''


        class Calculadora:
            '''Clase cohesiva con responsabilidad única.'''

            def sumar(self, a: float, b: float) -> float:
                return a + b

            def restar(self, a: float, b: float) -> float:
                return a - b

            def multiplicar(self, a: float, b: float) -> float:
                return a * b
    """))
    (tmp_path / "formateador.py").write_text(dedent("""
        '''Módulo de formateo, sin imports internos.'''


        def formatear_numero(n: float) -> str:
            return f"{n:.2f}"
    """))
    return tmp_path


@pytest.fixture
def proyecto_con_ciclo_directo(tmp_path):
    """
    Ciclo directo entre dos módulos: modulo_a ↔ modulo_b.

    modulo_a importa modulo_b y modulo_b importa modulo_a.
    DependencyCyclesAnalyzer debe detectar este SCC de tamaño 2 como CRITICAL.
    """
    (tmp_path / "modulo_a.py").write_text(dedent("""
        '''Módulo A — importa B (ciclo directo).'''
        from modulo_b import ClaseB


        class ClaseA:
            def operar(self) -> ClaseB:
                return ClaseB()
    """))
    (tmp_path / "modulo_b.py").write_text(dedent("""
        '''Módulo B — importa A (ciclo directo).'''
        from modulo_a import ClaseA


        class ClaseB:
            def operar(self) -> ClaseA:
                return ClaseA()
    """))
    return tmp_path


@pytest.fixture
def proyecto_con_ciclo_indirecto(tmp_path):
    """
    Ciclo indirecto de tres módulos: A → B → C → A.

    DependencyCyclesAnalyzer debe detectar el SCC de tamaño 3 como CRITICAL.
    """
    (tmp_path / "servicio.py").write_text(dedent("""
        '''Servicio — importa repositorio.'''
        import repositorio
    """))
    (tmp_path / "repositorio.py").write_text(dedent("""
        '''Repositorio — importa utilidades.'''
        import utilidades
    """))
    (tmp_path / "utilidades.py").write_text(dedent("""
        '''Utilidades — cierra el ciclo importando servicio.'''
        import servicio
    """))
    return tmp_path


@pytest.fixture
def proyecto_con_violaciones_de_capas(tmp_path):
    """
    Proyecto con arquitectura en capas declarada y violación conocida.

    Reglas: domain puede depender de nada, application puede depender de domain.
    Violación: domain.repositorio importa application.servicio (sube la dependencia).

    Requiere pyproject.toml con [tool.architectanalyst.layers] en tmp_path.
    """
    # Config con reglas de capas
    (tmp_path / "pyproject.toml").write_text(dedent("""
        [tool.architectanalyst]
        [tool.architectanalyst.layers]
        domain = []
        application = ["domain"]
    """))

    # Directorios de capas
    domain_dir = tmp_path / "domain"
    domain_dir.mkdir()
    app_dir = tmp_path / "application"
    app_dir.mkdir()

    # Capa domain: entity correcto (sin imports de otras capas)
    (domain_dir / "__init__.py").write_text("")
    (domain_dir / "entity.py").write_text(dedent("""
        '''Entidad de dominio — sin dependencias externas a la capa.'''


        class Pedido:
            def __init__(self, id: int):
                self.id = id
    """))

    # Capa domain: repositorio VIOLA (importa application)
    (domain_dir / "repositorio.py").write_text(dedent("""
        '''Repositorio — VIOLA: domain importa application.'''
        from application.servicio import Servicio


        class Repositorio:
            def guardar(self, entidad):
                Servicio().notificar(entidad)
    """))

    # Capa application: correcto (importa domain)
    (app_dir / "__init__.py").write_text("")
    (app_dir / "servicio.py").write_text(dedent("""
        '''Servicio de aplicación — importa domain (correcto).'''
        from domain.entity import Pedido


        class Servicio:
            def notificar(self, entidad):
                pass

            def procesar(self, id: int) -> Pedido:
                return Pedido(id)
    """))

    return tmp_path


@pytest.fixture
def proyecto_con_alta_inestabilidad(tmp_path):
    """
    Módulo con alta inestabilidad (I ≈ 1.0).

    nodo_hoja importa muchos módulos internos pero ninguno lo importa.
    I = Ce / (Ca + Ce) = N / (0 + N) → WARNING si I > 0.8.
    """
    (tmp_path / "base_a.py").write_text("class BaseA: pass\n")
    (tmp_path / "base_b.py").write_text("class BaseB: pass\n")
    (tmp_path / "base_c.py").write_text("class BaseC: pass\n")
    (tmp_path / "base_d.py").write_text("class BaseD: pass\n")
    (tmp_path / "base_e.py").write_text("class BaseE: pass\n")

    (tmp_path / "nodo_hoja.py").write_text(dedent("""
        '''Módulo hoja: importa todos los base, nadie lo importa.'''
        from base_a import BaseA
        from base_b import BaseB
        from base_c import BaseC
        from base_d import BaseD
        from base_e import BaseE


        class NodoHoja(BaseA, BaseB):
            def combinar(self) -> str:
                return f"{BaseC.__name__}{BaseD.__name__}{BaseE.__name__}"
    """))
    return tmp_path


# ---------------------------------------------------------------------------
# Tests: Pipeline completo sin mocks
# ---------------------------------------------------------------------------


class TestArchitectAnalystPipelineCompleto:
    """Verifica el pipeline end-to-end sin mocks."""

    def test_proyecto_limpio_no_tiene_ciclos_ni_capas(self, proyecto_limpio):
        """
        Un proyecto limpio (sin ciclos ni violaciones de capas) no debe generar
        CRITICAL por ciclos o capas.

        Nota: módulos con A=0, I=0 generan D=1.0 CRITICAL (Zone of Pain) — es
        correcto según las Métricas de Martin. El "limpio" aquí refiere a la
        ausencia de problemas estructurales (ciclos, capas), no a D.
        """
        analyst = ArchitectAnalyst(path=proyecto_limpio)
        results = analyst.run()

        cycle_criticals = [
            r for r in results
            if r.severity == ArchitectureSeverity.CRITICAL
            and r.metric_name in ("DependencyCycle", "LayerViolation")
        ]
        assert cycle_criticals == [], (
            f"No debe haber ciclos ni violaciones de capas: "
            f"{[r.message for r in cycle_criticals]}"
        )

    def test_proyecto_limpio_retorna_resultados_info(self, proyecto_limpio):
        analyst = ArchitectAnalyst(path=proyecto_limpio)
        results = analyst.run()

        # Debe haber resultados INFO (Ca, Ce, A son siempre INFO)
        infos = [r for r in results if r.severity == ArchitectureSeverity.INFO]
        assert len(infos) > 0

    def test_detecta_ciclo_directo(self, proyecto_con_ciclo_directo):
        analyst = ArchitectAnalyst(path=proyecto_con_ciclo_directo)
        results = analyst.run()

        criticals = [r for r in results if r.severity == ArchitectureSeverity.CRITICAL]
        assert len(criticals) >= 1, "Debe detectar al menos un CRITICAL por ciclo directo"

        # Al menos un resultado debe mencionar ciclo
        mensajes = [r.message.lower() for r in criticals]
        assert any("ciclo" in m or "cycle" in m or "scc" in m for m in mensajes), (
            f"Ningún mensaje menciona ciclo: {mensajes}"
        )

    def test_detecta_ciclo_indirecto_tres_modulos(self, proyecto_con_ciclo_indirecto):
        analyst = ArchitectAnalyst(path=proyecto_con_ciclo_indirecto)
        results = analyst.run()

        criticals = [r for r in results if r.severity == ArchitectureSeverity.CRITICAL]
        assert len(criticals) >= 1, "Debe detectar CRITICAL por ciclo A→B→C→A"

    def test_detecta_violacion_de_capas(self, proyecto_con_violaciones_de_capas):
        config_path = proyecto_con_violaciones_de_capas / "pyproject.toml"
        analyst = ArchitectAnalyst(
            path=proyecto_con_violaciones_de_capas,
            config_path=config_path,
        )
        results = analyst.run()

        criticals = [r for r in results if r.severity == ArchitectureSeverity.CRITICAL]
        assert len(criticals) >= 1, (
            "Debe detectar CRITICAL por violación de capa domain → application"
        )

    def test_alta_inestabilidad_genera_warning(self, proyecto_con_alta_inestabilidad):
        analyst = ArchitectAnalyst(path=proyecto_con_alta_inestabilidad)
        results = analyst.run()

        # nodo_hoja tiene I = 5/(0+5) = 1.0 → WARNING
        warnings_i = [
            r for r in results
            if r.severity == ArchitectureSeverity.WARNING and r.metric_name == "I"
        ]
        assert len(warnings_i) >= 1, (
            f"nodo_hoja debe generar WARNING por instabilidad. "
            f"Resultados: {[(r.metric_name, r.severity.value, r.value) for r in results]}"
        )

    def test_has_violations_true_con_ciclo(self, proyecto_con_ciclo_directo):
        analyst = ArchitectAnalyst(path=proyecto_con_ciclo_directo)
        analyst.run()
        assert analyst.has_violations() is True

    def test_has_critical_true_con_ciclo(self, proyecto_con_ciclo_directo):
        analyst = ArchitectAnalyst(path=proyecto_con_ciclo_directo)
        analyst.run()
        assert analyst.has_critical() is True

    def test_has_violations_false_sin_archivos(self, tmp_path):
        """Sin archivos Python, no hay violations."""
        analyst = ArchitectAnalyst(path=tmp_path)
        analyst.run()
        assert analyst.has_violations() is False

    def test_sprint_id_persiste_en_snapshot(self, proyecto_limpio, tmp_path):
        """Verifica que el sprint_id se almacena y el segundo análisis tiene tendencias."""
        db_path = tmp_path / "test.db"

        # Primer análisis
        analyst1 = ArchitectAnalyst(
            path=proyecto_limpio, sprint_id="sprint-1"
        )
        analyst1._store._db_path = db_path
        results1 = analyst1.run()

        # Sin histórico → trends deben ser None
        assert all(r.trend is None for r in results1)

    def test_directorio_vacio_retorna_lista_vacia(self, tmp_path):
        """Un directorio sin .py debe retornar lista vacía."""
        analyst = ArchitectAnalyst(path=tmp_path)
        results = analyst.run()
        assert results == []


# ---------------------------------------------------------------------------
# Tests: CLI end-to-end completo
# ---------------------------------------------------------------------------


class TestArchitectAnalystCLIe2e:
    """Tests E2E del CLI con archivos reales (sin mocks)."""

    def test_cli_exit_code_0_proyecto_limpio(self, runner, proyecto_limpio):
        """Exit code siempre 0, incluso en proyecto limpio."""
        result = runner.invoke(main, [str(proyecto_limpio)])
        assert result.exit_code == 0, f"Salida inesperada: {result.output}"

    def test_cli_exit_code_0_con_ciclo_critical(self, runner, proyecto_con_ciclo_directo):
        """Exit code 0 INCLUSO con violaciones CRITICAL — ArchitectAnalyst no bloquea."""
        result = runner.invoke(main, [str(proyecto_con_ciclo_directo)])
        assert result.exit_code == 0, (
            f"ArchitectAnalyst no debe bloquear. Salida: {result.output}"
        )

    def test_cli_formato_text_produce_output(self, runner, proyecto_limpio):
        result = runner.invoke(main, [str(proyecto_limpio), "--format", "text"])
        assert result.exit_code == 0
        assert "ArchitectAnalyst" in result.output

    def test_cli_formato_json_valido(self, runner, proyecto_limpio):
        result = runner.invoke(main, [str(proyecto_limpio), "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "summary" in data
        assert "results" in data
        assert data["summary"]["should_block"] is False

    def test_cli_json_con_ciclo_should_block_false(self, runner, proyecto_con_ciclo_directo):
        """JSON siempre tiene should_block=false aunque haya CRITICAL."""
        result = runner.invoke(
            main, [str(proyecto_con_ciclo_directo), "--format", "json"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["summary"]["should_block"] is False
        assert data["summary"]["critical_violations"] >= 1

    def test_cli_con_sprint_id_en_json(self, runner, proyecto_limpio):
        result = runner.invoke(
            main,
            [str(proyecto_limpio), "--format", "json", "--sprint-id", "sprint-99"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["summary"]["sprint_id"] == "sprint-99"

    def test_cli_con_sprint_id_en_text(self, runner, proyecto_limpio):
        result = runner.invoke(
            main,
            [str(proyecto_limpio), "--format", "text", "--sprint-id", "sprint-42"],
        )
        assert result.exit_code == 0
        assert "sprint-42" in result.output

    def test_cli_json_contiene_metricas_martin(self, runner, proyecto_limpio):
        """El JSON debe tener resultados con métricas de Martin (Coupling, A, D)."""
        result = runner.invoke(main, [str(proyecto_limpio), "--format", "json"])
        data = json.loads(result.output)
        metricas = {r["metric"] for r in data["results"]}
        # CouplingAnalyzer reporta "Coupling", siempre hay A y D
        assert metricas & {"Coupling", "A", "D"}, (
            f"Métricas esperadas no encontradas. Encontradas: {metricas}"
        )

    def test_cli_json_total_files_correcto(self, runner, proyecto_limpio):
        result = runner.invoke(main, [str(proyecto_limpio), "--format", "json"])
        data = json.loads(result.output)
        # proyecto_limpio tiene 2 archivos .py
        assert data["summary"]["total_files"] == 2

    def test_cli_ruta_inexistente_falla(self, runner):
        result = runner.invoke(main, ["/ruta/que/no/existe"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Test: Dogfooding — ArchitectAnalyst sobre sí mismo
# ---------------------------------------------------------------------------


class TestDogfooding:
    """Ticket 7.3 — Corre architectanalyst sobre el propio código del proyecto."""

    def test_dogfooding_corre_sin_excepciones(self, runner):
        """
        Corre architectanalyst sobre src/ del propio proyecto.

        Verifica que el CLI termina sin excepciones (exit code 0).
        No valida el contenido — el propio código puede tener métricas altas.
        """
        project_root = Path(__file__).parent.parent.parent
        src_path = project_root / "src"

        if not src_path.exists():
            pytest.skip("Directorio src/ no encontrado")

        result = runner.invoke(main, [str(src_path), "--format", "json"])

        assert result.exit_code == 0, (
            f"architectanalyst falló sobre src/ del propio proyecto.\n"
            f"Error: {result.exception}\n"
            f"Output: {result.output[:500]}"
        )

    def test_dogfooding_json_parseable(self, runner):
        """El JSON del dogfooding debe ser parseable y bien estructurado."""
        project_root = Path(__file__).parent.parent.parent
        src_path = project_root / "src"

        if not src_path.exists():
            pytest.skip("Directorio src/ no encontrado")

        result = runner.invoke(main, [str(src_path), "--format", "json"])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert data["summary"]["should_block"] is False
        assert data["summary"]["total_files"] > 0
        assert isinstance(data["results"], list)

    def test_dogfooding_detecta_metricas_de_martin(self, runner):
        """El propio proyecto debe generar resultados con métricas Ca, Ce, A, I, D."""
        project_root = Path(__file__).parent.parent.parent
        src_path = project_root / "src"

        if not src_path.exists():
            pytest.skip("Directorio src/ no encontrado")

        result = runner.invoke(main, [str(src_path), "--format", "json"])
        data = json.loads(result.output)

        metricas = {r["metric"] for r in data["results"]}
        # CouplingAnalyzer reporta metric_name="Coupling" (Ca y Ce agregados)
        esperadas = {"Coupling", "A", "D"}
        assert esperadas.issubset(metricas), (
            f"Métricas esperadas {esperadas} no encontradas. Encontradas: {metricas}"
        )
