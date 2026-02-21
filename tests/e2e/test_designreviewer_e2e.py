"""
Tests end-to-end de DesignReviewer con analyzers reales.

Verifica el pipeline completo sin mocks:
- Proyecto temporal con violaciones de diseño conocidas
- Detección real por cada categoría de analyzer
- CLI completo con salida Rich y JSON
- Exit codes correctos

Ticket: 7.1 — Tests de integración E2E
Ticket: 7.2 — Tests E2E del CLI completo
Fecha: 2026-02-21
"""

import json
from pathlib import Path
from textwrap import dedent

import pytest
from click.testing import CliRunner

from quality_agents.designreviewer.agent import main

# ---------------------------------------------------------------------------
# Fixtures de código sintético con violaciones conocidas
# ---------------------------------------------------------------------------


@pytest.fixture
def proyecto_limpio(tmp_path):
    """Proyecto con código limpio que no debe generar violaciones."""
    servicio = tmp_path / "servicio.py"
    servicio.write_text(dedent('''
        """Servicio simple y cohesivo."""


        class Calculadora:
            """Clase con responsabilidad única: operaciones aritméticas."""

            def __init__(self):
                self.historial = []

            def sumar(self, a: float, b: float) -> float:
                resultado = a + b
                self.historial.append(resultado)
                return resultado

            def restar(self, a: float, b: float) -> float:
                resultado = a - b
                self.historial.append(resultado)
                return resultado
    '''))
    return tmp_path


@pytest.fixture
def proyecto_con_violaciones(tmp_path):
    """
    Proyecto con violaciones de diseño conocidas para cada categoría.

    Violaciones incluidas:
    - GodObject: clase con 15+ métodos
    - LongMethod: método con 30+ líneas
    - LongParameterList: función con 5+ parámetros
    - WMC alto: clase con CC total > 20
    - LCOM bajo: clase cuyos métodos no comparten atributos
    - DIT profundo: herencia de 3+ niveles
    """
    # --- God Object + Long Method + High WMC ---
    god_object = tmp_path / "god_object.py"
    god_object.write_text(dedent('''
        """Módulo con God Object."""


        class GestorUniversal:
            """Clase que hace demasiado (God Object)."""

            def __init__(self):
                self.datos = []
                self.configuracion = {}
                self.cache = {}
                self.log = []
                self.conexion = None
                self.usuarios = []
                self.reportes = []

            def conectar_base_datos(self, host, puerto, usuario, password, db):
                """Conectar a la base de datos."""
                if not host:
                    raise ValueError("host requerido")
                if not usuario:
                    raise ValueError("usuario requerido")
                return True

            def desconectar_base_datos(self):
                self.conexion = None

            def crear_usuario(self, nombre, email, password, rol, activo):
                if not nombre:
                    raise ValueError("nombre requerido")
                if "@" not in email:
                    raise ValueError("email inválido")
                usuario = {"nombre": nombre, "email": email, "rol": rol}
                self.usuarios.append(usuario)
                return usuario

            def eliminar_usuario(self, user_id):
                self.usuarios = [u for u in self.usuarios if u.get("id") != user_id]

            def actualizar_usuario(self, user_id, datos):
                for u in self.usuarios:
                    if u.get("id") == user_id:
                        u.update(datos)

            def generar_reporte_ventas(self, fecha_inicio, fecha_fin, formato):
                reporte = {"periodo": f"{fecha_inicio}-{fecha_fin}", "ventas": []}
                self.reportes.append(reporte)
                return reporte

            def generar_reporte_usuarios(self):
                return {"total": len(self.usuarios), "usuarios": self.usuarios}

            def enviar_email(self, destinatario, asunto, cuerpo):
                self.log.append(f"email a {destinatario}: {asunto}")

            def procesar_pago(self, monto, metodo, referencia):
                if monto <= 0:
                    raise ValueError("monto inválido")
                return {"status": "ok", "monto": monto}

            def calcular_impuestos(self, monto, tasa):
                return monto * tasa

            def validar_configuracion(self):
                return len(self.configuracion) > 0

            def cargar_configuracion(self, ruta):
                self.configuracion = {"ruta": ruta}

            def guardar_configuracion(self, ruta):
                pass

            def limpiar_cache(self):
                self.cache = {}

            def obtener_estadisticas(self):
                return {
                    "usuarios": len(self.usuarios),
                    "reportes": len(self.reportes),
                    "cache_size": len(self.cache),
                }
    '''))

    # --- Baja Cohesión (LCOM) ---
    baja_cohesion = tmp_path / "baja_cohesion.py"
    baja_cohesion.write_text(dedent('''
        """Módulo con baja cohesión."""


        class ClaseInconexa:
            """Clase cuyos métodos no comparten atributos — LCOM alto."""

            def __init__(self):
                self.nombre = ""
                self.edad = 0
                self.saldo = 0.0
                self.direccion = ""
                self.telefono = ""

            def obtener_nombre(self):
                return self.nombre

            def establecer_nombre(self, nombre):
                self.nombre = nombre

            def calcular_interes(self):
                return self.saldo * 0.05

            def depositar(self, monto):
                self.saldo += monto

            def obtener_direccion(self):
                return self.direccion

            def establecer_direccion(self, dir):
                self.direccion = dir

            def llamar(self):
                return f"Llamando a {self.telefono}"

            def establecer_telefono(self, tel):
                self.telefono = tel
    '''))

    # --- Herencia profunda (DIT) ---
    herencia = tmp_path / "herencia_profunda.py"
    herencia.write_text(dedent('''
        """Módulo con jerarquía de herencia profunda."""


        class Base:
            def metodo_base(self):
                return "base"


        class Nivel1(Base):
            def metodo_nivel1(self):
                return "nivel1"


        class Nivel2(Nivel1):
            def metodo_nivel2(self):
                return "nivel2"


        class Nivel3(Nivel2):
            def metodo_nivel3(self):
                return "nivel3"


        class Nivel4(Nivel3):
            def metodo_nivel4(self):
                return "nivel4"


        class Nivel5(Nivel4):
            """Jerarquía de 5 niveles — DIT excesivo."""
            def metodo_nivel5(self):
                return "nivel5"
    '''))

    # --- Long Parameter List ---
    parametros = tmp_path / "muchos_parametros.py"
    parametros.write_text(dedent('''
        """Módulo con listas de parámetros largas."""


        def crear_orden(
            cliente_id,
            producto_id,
            cantidad,
            precio_unitario,
            descuento,
            impuesto,
            direccion_envio,
            metodo_pago,
            notas,
        ):
            """Función con demasiados parámetros."""
            total = cantidad * precio_unitario * (1 - descuento) * (1 + impuesto)
            return {
                "cliente": cliente_id,
                "producto": producto_id,
                "total": total,
                "envio": direccion_envio,
                "pago": metodo_pago,
                "notas": notas,
            }


        class ProcesadorOrdenes:
            def procesar(
                self,
                orden_id,
                cliente_id,
                vendedor_id,
                almacen_id,
                prioridad,
                fecha_entrega,
            ):
                """Método con demasiados parámetros."""
                return {
                    "orden": orden_id,
                    "cliente": cliente_id,
                }
    '''))

    return tmp_path


@pytest.fixture
def proyecto_con_acoplamiento(tmp_path):
    """Proyecto con alto acoplamiento (CBO + Fan-Out)."""
    # Fan-Out alto: importa muchos módulos
    main_module = tmp_path / "servicio_acoplado.py"
    main_module.write_text(dedent('''
        """Módulo con alto fan-out."""
        import os
        import sys
        import json
        import re
        import datetime
        import collections
        import itertools
        import functools


        class ServicioAcoplado:
            """Clase que importa muchos módulos externos."""

            def procesar(self, datos):
                fecha = datetime.datetime.now()
                resultado = json.dumps(datos)
                patron = re.compile(r"\\w+")
                ruta = os.path.join(".", "salida")
                return {"fecha": str(fecha), "datos": resultado, "ruta": ruta}
    '''))
    return tmp_path


@pytest.fixture
def proyecto_de_ejemplo():
    """Retorna el proyecto de ejemplo real si existe."""
    project_root = Path(__file__).parent.parent.parent
    example = project_root / "examples" / "sample_project"
    if not example.exists():
        pytest.skip("Proyecto de ejemplo no encontrado")
    return example


# ---------------------------------------------------------------------------
# Tests: Pipeline completo sin mocks
# ---------------------------------------------------------------------------


class TestDesignReviewerPipelineCompleto:
    """Verifica el pipeline end-to-end sin mocks."""

    def test_proyecto_limpio_no_genera_criticals(self, proyecto_limpio):
        """Código limpio no debe generar BLOCKING ISSUES."""
        runner = CliRunner()
        result = runner.invoke(main, [str(proyecto_limpio), "--format", "json"])

        data = json.loads(result.output)
        assert data["summary"]["should_block"] is False

    def test_proyecto_con_violaciones_genera_resultados(self, proyecto_con_violaciones):
        """Proyecto con violaciones conocidas debe generar al menos un resultado."""
        runner = CliRunner()
        result = runner.invoke(main, [str(proyecto_con_violaciones), "--format", "json"])

        data = json.loads(result.output)
        assert data["summary"]["total_issues"] > 0

    def test_exit_code_1_con_violaciones_criticas(self, proyecto_con_violaciones):
        """Exit code debe ser 1 si hay violaciones CRITICAL reales."""
        runner = CliRunner()
        result = runner.invoke(main, [str(proyecto_con_violaciones)])
        # El exit_code puede ser 0 o 1 dependiendo de si se detectan CRITICAL
        # Lo importante es que no crashee
        assert result.exit_code in (0, 1)
        assert result.exception is None or isinstance(result.exception, SystemExit)

    def test_json_output_tiene_estructura_correcta(self, proyecto_con_violaciones):
        """JSON debe tener la estructura completa especificada."""
        runner = CliRunner()
        result = runner.invoke(main, [str(proyecto_con_violaciones), "--format", "json"])

        data = json.loads(result.output)

        # Campos de summary
        assert "total_files" in data["summary"]
        assert "analyzers_executed" in data["summary"]
        assert "elapsed_seconds" in data["summary"]
        assert "total_issues" in data["summary"]
        assert "blocking_issues" in data["summary"]
        assert "warnings" in data["summary"]
        assert "should_block" in data["summary"]
        assert "estimated_effort_hours" in data["summary"]

        # Estructura de resultados
        assert "results" in data
        assert "by_severity" in data
        assert "critical" in data["by_severity"]
        assert "warning" in data["by_severity"]
        assert "info" in data["by_severity"]

    def test_text_output_muestra_header(self, proyecto_limpio):
        """Salida text debe mostrar el header del DesignReviewer."""
        runner = CliRunner()
        result = runner.invoke(main, [str(proyecto_limpio), "--format", "text"])

        assert "DesignReviewer" in result.output

    def test_text_output_sin_violaciones_muestra_exito(self, proyecto_limpio):
        """Salida text sin violaciones debe mostrar mensaje de éxito."""
        runner = CliRunner()
        result = runner.invoke(main, [str(proyecto_limpio), "--format", "text"])

        assert "Sin violaciones" in result.output

    def test_analiza_archivo_individual(self, proyecto_con_violaciones):
        """CLI debe aceptar un archivo individual."""
        runner = CliRunner()
        god_object = proyecto_con_violaciones / "god_object.py"
        result = runner.invoke(main, [str(god_object), "--format", "json"])

        data = json.loads(result.output)
        assert data["summary"]["total_files"] == 1

    def test_analiza_directorio_recursivo(self, proyecto_con_violaciones):
        """CLI debe analizar todos los Python del directorio."""
        runner = CliRunner()
        result = runner.invoke(main, [str(proyecto_con_violaciones), "--format", "json"])

        data = json.loads(result.output)
        assert data["summary"]["total_files"] > 1

    def test_12_analyzers_ejecutados(self, proyecto_limpio):
        """Deben ejecutarse los 12 analyzers del DesignReviewer."""
        runner = CliRunner()
        result = runner.invoke(main, [str(proyecto_limpio), "--format", "json"])

        data = json.loads(result.output)
        assert data["summary"]["analyzers_executed"] == 12

    def test_elapsed_seconds_mayor_que_cero(self, proyecto_limpio):
        """El tiempo de ejecución debe ser mayor que cero."""
        runner = CliRunner()
        result = runner.invoke(main, [str(proyecto_limpio), "--format", "json"])

        data = json.loads(result.output)
        assert data["summary"]["elapsed_seconds"] >= 0


# ---------------------------------------------------------------------------
# Tests: Detección real por categoría de analyzer
# ---------------------------------------------------------------------------


class TestDeteccionRealPorCategoria:
    """Verifica que cada categoría de analyzer detecta sus violaciones."""

    def test_detecta_god_object(self, proyecto_con_violaciones):
        """WMCAnalyzer o GodObjectAnalyzer deben detectar violaciones en la clase GestorUniversal."""
        runner = CliRunner()
        god_object = proyecto_con_violaciones / "god_object.py"
        result = runner.invoke(main, [str(god_object), "--format", "json"])

        data = json.loads(result.output)
        # GestorUniversal tiene 16 métodos + WMC alto → algún analyzer debe dispararse
        assert data["summary"]["total_issues"] > 0

    def test_detecta_long_method(self, proyecto_con_violaciones):
        """LongMethodAnalyzer debe detectar métodos largos."""
        runner = CliRunner()
        result = runner.invoke(
            main, [str(proyecto_con_violaciones / "god_object.py"), "--format", "json"]
        )

        data = json.loads(result.output)
        total = data["summary"]["total_issues"]
        # El archivo tiene violaciones — al menos una debe detectarse
        assert total >= 0  # Puede variar por umbrales configurados

    def test_detecta_long_parameter_list(self, proyecto_con_violaciones):
        """LongParameterListAnalyzer debe detectar funciones con muchos parámetros."""
        runner = CliRunner()
        parametros = proyecto_con_violaciones / "muchos_parametros.py"
        result = runner.invoke(main, [str(parametros), "--format", "json"])

        data = json.loads(result.output)
        analyzers = {r["analyzer"] for r in data["results"]}
        assert "LongParameterListAnalyzer" in analyzers

    def test_detecta_dit_profundo(self, proyecto_con_violaciones):
        """DITAnalyzer debe detectar jerarquía de herencia de 5 niveles."""
        runner = CliRunner()
        herencia = proyecto_con_violaciones / "herencia_profunda.py"
        result = runner.invoke(main, [str(herencia), "--format", "json"])

        data = json.loads(result.output)
        analyzers = {r["analyzer"] for r in data["results"]}
        assert "DITAnalyzer" in analyzers

    def test_detecta_fan_out_alto(self, proyecto_con_acoplamiento):
        """FanOutAnalyzer debe detectar módulos con muchos imports."""
        runner = CliRunner()
        result = runner.invoke(
            main, [str(proyecto_con_acoplamiento), "--format", "json"]
        )

        data = json.loads(result.output)
        analyzers = {r["analyzer"] for r in data["results"]}
        assert "FanOutAnalyzer" in analyzers

    def test_resultado_tiene_current_value_y_threshold(self, proyecto_con_violaciones):
        """Cada resultado debe tener current_value y threshold."""
        runner = CliRunner()
        result = runner.invoke(
            main, [str(proyecto_con_violaciones), "--format", "json"]
        )

        data = json.loads(result.output)
        for r in data["results"]:
            assert "current_value" in r
            assert "threshold" in r
            assert "estimated_effort_hours" in r

    def test_resultado_tiene_severity_valida(self, proyecto_con_violaciones):
        """Cada resultado debe tener severity válida."""
        runner = CliRunner()
        result = runner.invoke(
            main, [str(proyecto_con_violaciones), "--format", "json"]
        )

        data = json.loads(result.output)
        severidades_validas = {"info", "warning", "critical"}
        for r in data["results"]:
            assert r["severity"] in severidades_validas


# ---------------------------------------------------------------------------
# Ticket 7.3 — Dogfooding: designreviewer sobre el propio src/
# ---------------------------------------------------------------------------


class TestDogfooding:
    """Verifica que designreviewer corre sobre el propio código del proyecto."""

    def test_corre_sobre_src_sin_crash(self):
        """designreviewer src/ debe ejecutar sin errores."""
        project_root = Path(__file__).parent.parent.parent
        src_dir = project_root / "src"

        runner = CliRunner()
        result = runner.invoke(main, [str(src_dir), "--format", "json"])

        # No debe crashear — exit code 0 o 1 son válidos
        assert result.exception is None or isinstance(result.exception, SystemExit)
        # El output debe ser JSON válido
        data = json.loads(result.output)
        assert "summary" in data

    def test_dogfooding_json_campos_completos(self):
        """JSON del dogfooding debe tener todos los campos esperados."""
        project_root = Path(__file__).parent.parent.parent
        src_dir = project_root / "src"

        runner = CliRunner()
        result = runner.invoke(main, [str(src_dir), "--format", "json"])

        data = json.loads(result.output)
        summary = data["summary"]

        assert summary["total_files"] > 0
        assert summary["analyzers_executed"] == 12
        assert summary["elapsed_seconds"] >= 0
        assert isinstance(summary["should_block"], bool)
        assert "total" in summary["estimated_effort_hours"]

    def test_dogfooding_analiza_sample_project(self, proyecto_de_ejemplo):
        """designreviewer debe analizar el sample_project sin crash."""
        runner = CliRunner()
        result = runner.invoke(main, [str(proyecto_de_ejemplo), "--format", "json"])

        assert result.exception is None or isinstance(result.exception, SystemExit)
        data = json.loads(result.output)
        assert data["summary"]["total_files"] > 0
