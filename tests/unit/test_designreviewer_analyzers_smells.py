"""
Tests unitarios para los analyzers de code smells de DesignReviewer (Fase 4).

Cubre GodObjectAnalyzer, LongMethodAnalyzer, LongParameterListAnalyzer,
FeatureEnvyAnalyzer y DataClumpsAnalyzer usando fixtures de código Python
sintético escritos inline con tmp_path.

Ticket: 4.6
"""

import textwrap
from pathlib import Path

import pytest

from quality_agents.designreviewer.analyzers.data_clumps_analyzer import DataClumpsAnalyzer
from quality_agents.designreviewer.analyzers.feature_envy_analyzer import FeatureEnvyAnalyzer
from quality_agents.designreviewer.analyzers.god_object_analyzer import GodObjectAnalyzer
from quality_agents.designreviewer.analyzers.long_method_analyzer import LongMethodAnalyzer
from quality_agents.designreviewer.analyzers.long_parameter_list_analyzer import (
    LongParameterListAnalyzer,
)
from quality_agents.designreviewer.config import DesignReviewerConfig
from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity, SolidPrinciple
from quality_agents.designreviewer.orchestrator import AnalyzerOrchestrator
from quality_agents.shared.verifiable import ExecutionContext


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _py(tmp_path: Path, nombre: str, codigo: str) -> Path:
    """Crea un archivo .py en tmp_path con el código dado (dedentado)."""
    archivo = tmp_path / nombre
    archivo.write_text(textwrap.dedent(codigo))
    return archivo


def _ejecutar(analyzer, archivo: Path, config: DesignReviewerConfig) -> list[ReviewResult]:
    """Inicializa contexto, llama should_run y execute."""
    ctx = ExecutionContext(file_path=archivo, config=config)
    analyzer.should_run(ctx)
    return analyzer.execute(archivo)


# ─────────────────────────────────────────────────────────────────────────────
# GodObjectAnalyzer
# ─────────────────────────────────────────────────────────────────────────────

class TestGodObjectAnalyzer:

    def test_detecta_violacion_por_metodos(self, tmp_path):
        """Clase con más métodos que el umbral debe ser detectada."""
        f = _py(tmp_path, "god_metodos.py", """
            class ClaseDios:
                def metodo_a(self): pass
                def metodo_b(self): pass
                def metodo_c(self): pass
                def metodo_d(self): pass
                def metodo_e(self): pass
        """)
        config = DesignReviewerConfig(max_god_object_methods=4, max_god_object_lines=500)
        results = _ejecutar(GodObjectAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.CRITICAL
        assert results[0].class_name == "ClaseDios"
        assert results[0].current_value == 5

    def test_detecta_violacion_por_lineas(self, tmp_path):
        """Clase con más líneas que el umbral (pero pocos métodos) debe ser detectada."""
        f = _py(tmp_path, "god_lineas.py", """
            class ClaseGrande:
                def unico(self):
                    # relleno 1
                    # relleno 2
                    # relleno 3
                    # relleno 4
                    # relleno 5
                    # relleno 6
                    # relleno 7
                    # relleno 8
                    return None
        """)
        config = DesignReviewerConfig(max_god_object_methods=50, max_god_object_lines=8)
        results = _ejecutar(GodObjectAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.CRITICAL
        assert results[0].class_name == "ClaseGrande"

    def test_detecta_ambas_violaciones_en_mensaje(self, tmp_path):
        """Si viola ambos umbrales, el mensaje debe mencionar ambos."""
        f = _py(tmp_path, "god_ambas.py", """
            class DobleViolacion:
                def m1(self): pass
                def m2(self): pass
                def m3(self): pass
                def m4(self): pass
                def m5(self):
                    # padding
                    # padding
                    # padding
                    return None
        """)
        config = DesignReviewerConfig(max_god_object_methods=3, max_god_object_lines=5)
        results = _ejecutar(GodObjectAnalyzer(), f, config)

        assert len(results) == 1
        assert "métodos" in results[0].message
        assert "líneas" in results[0].message

    def test_no_detecta_clase_dentro_de_umbrales(self, tmp_path):
        """Clase con pocos métodos y pocas líneas no debe ser detectada."""
        f = _py(tmp_path, "normal.py", """
            class ClaseNormal:
                def obtener(self): return self.valor
                def guardar(self, v): self.valor = v
        """)
        config = DesignReviewerConfig(max_god_object_methods=10, max_god_object_lines=100)
        results = _ejecutar(GodObjectAnalyzer(), f, config)

        assert results == []

    def test_excluye_metodos_dunder(self, tmp_path):
        """Los métodos dunder (__init__, __str__, etc.) no cuentan como métodos."""
        f = _py(tmp_path, "dunders.py", """
            class ConDunders:
                def __init__(self): pass
                def __str__(self): return ""
                def __repr__(self): return ""
                def __eq__(self, other): return True
                def __hash__(self): return 0
                def publico(self): pass
        """)
        # Solo 1 método no-dunder: publico → no viola umbral 3
        config = DesignReviewerConfig(max_god_object_methods=3, max_god_object_lines=500)
        results = _ejecutar(GodObjectAnalyzer(), f, config)

        assert results == []

    def test_cuenta_metodos_privados(self, tmp_path):
        """Los métodos privados (_nombre) sí cuentan como métodos."""
        f = _py(tmp_path, "privados.py", """
            class ConPrivados:
                def _privado_a(self): pass
                def _privado_b(self): pass
                def _privado_c(self): pass
                def _privado_d(self): pass
        """)
        # 4 métodos _privados > umbral 3
        config = DesignReviewerConfig(max_god_object_methods=3, max_god_object_lines=500)
        results = _ejecutar(GodObjectAnalyzer(), f, config)

        assert len(results) == 1

    def test_estimated_effort_formula(self, tmp_path):
        """estimated_effort debe ser 3.0 + exceso_metodos * 0.5."""
        f = _py(tmp_path, "effort.py", """
            class Clase:
                def m1(self): pass
                def m2(self): pass
                def m3(self): pass
                def m4(self): pass
                def m5(self): pass
                def m6(self): pass
        """)
        # 6 métodos, umbral 4 → exceso = 2
        config = DesignReviewerConfig(max_god_object_methods=4, max_god_object_lines=500)
        results = _ejecutar(GodObjectAnalyzer(), f, config)

        assert len(results) == 1
        exceso = 6 - 4
        assert results[0].estimated_effort == round(3.0 + exceso * 0.5, 1)

    def test_archivo_con_error_de_sintaxis(self, tmp_path):
        """Archivo con error de sintaxis debe retornar lista vacía sin lanzar."""
        f = _py(tmp_path, "roto.py", "def roto(\n")
        config = DesignReviewerConfig()
        results = _ejecutar(GodObjectAnalyzer(), f, config)

        assert results == []

    def test_umbral_personalizado(self, tmp_path):
        """Debe respetar el umbral configurado."""
        f = _py(tmp_path, "umbral.py", """
            class Clase:
                def a(self): pass
                def b(self): pass
                def c(self): pass
        """)
        # 3 métodos: viola umbral 2, no viola umbral 5
        assert len(_ejecutar(GodObjectAnalyzer(), f,
                             DesignReviewerConfig(max_god_object_methods=2,
                                                  max_god_object_lines=500))) == 1
        assert len(_ejecutar(GodObjectAnalyzer(), f,
                             DesignReviewerConfig(max_god_object_methods=5,
                                                  max_god_object_lines=500))) == 0


# ─────────────────────────────────────────────────────────────────────────────
# LongMethodAnalyzer
# ─────────────────────────────────────────────────────────────────────────────

class TestLongMethodAnalyzer:

    def test_detecta_metodo_largo_en_clase(self, tmp_path):
        """Método de clase con más líneas que el umbral debe ser detectado."""
        f = _py(tmp_path, "metodo_largo.py", """
            class Clase:
                def largo(self):
                    x = 1
                    y = 2
                    z = 3
                    a = 4
                    b = 5
                    return x + y + z + a + b
        """)
        config = DesignReviewerConfig(max_method_lines=5)
        results = _ejecutar(LongMethodAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.WARNING
        assert results[0].class_name == "Clase"
        assert "Clase.largo" in results[0].message

    def test_detecta_funcion_de_modulo_larga(self, tmp_path):
        """Función de módulo (fuera de clase) larga también debe detectarse."""
        f = _py(tmp_path, "funcion_larga.py", """
            def procesar(datos):
                resultado = []
                for d in datos:
                    resultado.append(d)
                total = len(resultado)
                return total
        """)
        config = DesignReviewerConfig(max_method_lines=4)
        results = _ejecutar(LongMethodAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].class_name is None
        assert "procesar" in results[0].message

    def test_no_detecta_metodo_dentro_del_umbral(self, tmp_path):
        """Método con exactamente el umbral de líneas no debe reportarse."""
        f = _py(tmp_path, "corto.py", """
            class Clase:
                def corto(self):
                    x = 1
                    return x
        """)
        config = DesignReviewerConfig(max_method_lines=10)
        results = _ejecutar(LongMethodAnalyzer(), f, config)

        assert results == []

    def test_nombre_incluye_clase_y_metodo(self, tmp_path):
        """El mensaje debe incluir 'Clase.metodo' para métodos de clase."""
        f = _py(tmp_path, "nombre.py", """
            class MiClase:
                def mi_metodo(self):
                    a = 1
                    b = 2
                    c = 3
                    d = 4
                    return a + b + c + d
        """)
        config = DesignReviewerConfig(max_method_lines=3)
        results = _ejecutar(LongMethodAnalyzer(), f, config)

        assert len(results) == 1
        assert "MiClase.mi_metodo" in results[0].message

    def test_estimated_effort_formula(self, tmp_path):
        """estimated_effort debe ser exceso / 10 * 0.5."""
        f = _py(tmp_path, "effort.py", """
            def funcion():
                a = 1
                b = 2
                c = 3
                d = 4
                e = 5
                f = 6
                g = 7
                h = 8
                i = 9
                j = 10
                k = 11
                return a
        """)
        # umbral = 5, líneas = 14 → exceso = 9
        config = DesignReviewerConfig(max_method_lines=5)
        results = _ejecutar(LongMethodAnalyzer(), f, config)

        assert len(results) == 1
        lineas = results[0].current_value
        exceso = lineas - 5
        assert results[0].estimated_effort == round(exceso / 10 * 0.5, 1)

    def test_archivo_con_error_de_sintaxis(self, tmp_path):
        """Archivo con error de sintaxis debe retornar lista vacía sin lanzar."""
        f = _py(tmp_path, "roto.py", "def roto(\n")
        results = _ejecutar(LongMethodAnalyzer(), f, DesignReviewerConfig())

        assert results == []

    def test_umbral_personalizado(self, tmp_path):
        """Debe respetar el umbral configurado."""
        f = _py(tmp_path, "umbral.py", """
            def funcion():
                a = 1
                b = 2
                c = 3
                d = 4
                e = 5
                return a
        """)
        # ~8 líneas: viola umbral 5, no viola umbral 20
        assert len(_ejecutar(LongMethodAnalyzer(), f,
                             DesignReviewerConfig(max_method_lines=5))) == 1
        assert len(_ejecutar(LongMethodAnalyzer(), f,
                             DesignReviewerConfig(max_method_lines=20))) == 0


# ─────────────────────────────────────────────────────────────────────────────
# LongParameterListAnalyzer
# ─────────────────────────────────────────────────────────────────────────────

class TestLongParameterListAnalyzer:

    def test_detecta_metodo_con_muchos_params(self, tmp_path):
        """Método con más parámetros que el umbral debe ser detectado."""
        f = _py(tmp_path, "params.py", """
            class Clase:
                def metodo(self, a, b, c, d): pass
        """)
        config = DesignReviewerConfig(max_parameters=3)
        results = _ejecutar(LongParameterListAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.WARNING
        assert results[0].current_value == 4

    def test_detecta_funcion_de_modulo(self, tmp_path):
        """Función de módulo con muchos parámetros debe ser detectada."""
        f = _py(tmp_path, "funcion_params.py", """
            def crear(nombre, apellido, edad, email, telefono): pass
        """)
        config = DesignReviewerConfig(max_parameters=3)
        results = _ejecutar(LongParameterListAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].class_name is None

    def test_excluye_self_y_cls(self, tmp_path):
        """self y cls no deben contar en el total de parámetros."""
        f = _py(tmp_path, "self_cls.py", """
            class Clase:
                def instancia(self, a, b): pass
                def de_clase(cls, a, b): pass
        """)
        # self/cls excluidos → cada método tiene 2 params → no viola umbral 3
        config = DesignReviewerConfig(max_parameters=3)
        results = _ejecutar(LongParameterListAnalyzer(), f, config)

        assert results == []

    def test_no_cuenta_args_y_kwargs(self, tmp_path):
        """*args y **kwargs no deben contar como parámetros."""
        f = _py(tmp_path, "varargs.py", """
            def funcion(a, b, *args, **kwargs): pass
        """)
        # Solo 2 params reales (a, b) → no viola umbral 3
        config = DesignReviewerConfig(max_parameters=3)
        results = _ejecutar(LongParameterListAnalyzer(), f, config)

        assert results == []

    def test_cuenta_params_solo_posicionales(self, tmp_path):
        """Los parámetros solo-posicionales (antes de /) sí deben contar."""
        f = _py(tmp_path, "posonly.py", """
            def funcion(a, b, /, c, d): pass
        """)
        # a, b (posonly) + c, d (normal) = 4 params > umbral 3
        config = DesignReviewerConfig(max_parameters=3)
        results = _ejecutar(LongParameterListAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].current_value == 4

    def test_cuenta_params_solo_keyword(self, tmp_path):
        """Los parámetros solo-keyword (después de *) sí deben contar."""
        f = _py(tmp_path, "kwonly.py", """
            def funcion(a, *, b, c, d): pass
        """)
        # a (normal) + b, c, d (kwonly) = 4 params > umbral 3
        config = DesignReviewerConfig(max_parameters=3)
        results = _ejecutar(LongParameterListAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].current_value == 4

    def test_archivo_con_error_de_sintaxis(self, tmp_path):
        """Archivo con error de sintaxis debe retornar lista vacía."""
        f = _py(tmp_path, "roto.py", "def roto(\n")
        results = _ejecutar(LongParameterListAnalyzer(), f, DesignReviewerConfig())

        assert results == []

    def test_umbral_personalizado(self, tmp_path):
        """Debe respetar el umbral configurado."""
        f = _py(tmp_path, "umbral.py", """
            def funcion(a, b, c, d): pass
        """)
        # 4 params: viola umbral 3, no viola umbral 5
        assert len(_ejecutar(LongParameterListAnalyzer(), f,
                             DesignReviewerConfig(max_parameters=3))) == 1
        assert len(_ejecutar(LongParameterListAnalyzer(), f,
                             DesignReviewerConfig(max_parameters=5))) == 0


# ─────────────────────────────────────────────────────────────────────────────
# FeatureEnvyAnalyzer
# ─────────────────────────────────────────────────────────────────────────────

class TestFeatureEnvyAnalyzer:

    def test_detecta_feature_envy_basico(self, tmp_path):
        """Método que accede más a un parámetro que a self debe ser detectado."""
        f = _py(tmp_path, "envy.py", """
            class Reporte:
                def generar(self, orden):
                    items = orden.items
                    total = orden.total
                    cliente = orden.cliente
                    self.log.info("ok")
                    return f"{cliente}: {total}"
        """)
        results = _ejecutar(FeatureEnvyAnalyzer(), f, DesignReviewerConfig())

        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.WARNING
        assert results[0].class_name == "Reporte"
        assert "Reporte.generar" in results[0].message
        assert "orden" in results[0].message

    def test_no_detecta_cuando_self_domina(self, tmp_path):
        """Método donde self es accedido más que los parámetros no debe detectarse."""
        f = _py(tmp_path, "self_domina.py", """
            class Servicio:
                def procesar(self, config):
                    self.estado = True
                    self.log = []
                    self.resultado = self.calcular()
                    self.flag = config.valor
                    return self.resultado
        """)
        results = _ejecutar(FeatureEnvyAnalyzer(), f, DesignReviewerConfig())

        assert results == []

    def test_no_detecta_pocos_accesos_externos(self, tmp_path):
        """Método con menos de 3 accesos a un parámetro no debe detectarse."""
        f = _py(tmp_path, "pocos_accesos.py", """
            class Clase:
                def metodo(self, obj):
                    return obj.valor  # Solo 1 acceso a obj → no es Feature Envy
        """)
        results = _ejecutar(FeatureEnvyAnalyzer(), f, DesignReviewerConfig())

        assert results == []

    def test_excluye_metodos_dunder(self, tmp_path):
        """Los métodos dunder deben ser excluidos del análisis."""
        f = _py(tmp_path, "dunder.py", """
            class Clase:
                def __init__(self, db):
                    self.x = db.conn
                    self.y = db.host
                    self.z = db.port
                    self.w = db.name
                    self.v = db.user
        """)
        # __init__ accede más a db que a self, pero es dunder → no detectar
        results = _ejecutar(FeatureEnvyAnalyzer(), f, DesignReviewerConfig())

        assert results == []

    def test_identifica_el_param_mas_accedido(self, tmp_path):
        """El mensaje debe nombrar el parámetro con más accesos."""
        f = _py(tmp_path, "param_max.py", """
            class Procesador:
                def ejecutar(self, config, orden):
                    # orden accedido 4 veces, config 1 vez
                    x = orden.items
                    y = orden.total
                    z = orden.estado
                    w = orden.fecha
                    c = config.modo
                    return x
        """)
        results = _ejecutar(FeatureEnvyAnalyzer(), f, DesignReviewerConfig())

        assert len(results) == 1
        assert "orden" in results[0].message

    def test_no_detecta_metodo_sin_params_externos(self, tmp_path):
        """Método con solo self no puede tener Feature Envy."""
        f = _py(tmp_path, "solo_self.py", """
            class Clase:
                def sin_params(self):
                    return self.valor + self.otro + self.mas
        """)
        results = _ejecutar(FeatureEnvyAnalyzer(), f, DesignReviewerConfig())

        assert results == []

    def test_solid_principle_y_smell_type(self, tmp_path):
        """El resultado debe tener solid_principle=SRP y smell_type=FeatureEnvy."""
        f = _py(tmp_path, "solid.py", """
            class R:
                def m(self, obj):
                    a = obj.a
                    b = obj.b
                    c = obj.c
                    return a + b + c
        """)
        results = _ejecutar(FeatureEnvyAnalyzer(), f, DesignReviewerConfig())

        assert len(results) == 1
        assert results[0].solid_principle == SolidPrinciple.SRP
        assert results[0].smell_type == "FeatureEnvy"

    def test_archivo_con_error_de_sintaxis(self, tmp_path):
        """Archivo con error de sintaxis debe retornar lista vacía."""
        f = _py(tmp_path, "roto.py", "def roto(\n")
        results = _ejecutar(FeatureEnvyAnalyzer(), f, DesignReviewerConfig())

        assert results == []


# ─────────────────────────────────────────────────────────────────────────────
# DataClumpsAnalyzer
# ─────────────────────────────────────────────────────────────────────────────

class TestDataClumpsAnalyzer:

    def test_detecta_clump_simple(self, tmp_path):
        """Tres parámetros que aparecen en 2 funciones deben reportarse."""
        f = _py(tmp_path, "clump.py", """
            def conectar(host, port, timeout): pass
            def reconectar(host, port, timeout): pass
        """)
        config = DesignReviewerConfig(min_data_clump_size=3, min_data_clump_occurrences=2)
        results = _ejecutar(DataClumpsAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.WARNING
        assert "host" in results[0].message
        assert "port" in results[0].message
        assert "timeout" in results[0].message

    def test_no_detecta_grupo_de_dos_params(self, tmp_path):
        """Un grupo de solo 2 parámetros no debe reportarse (min_size=3)."""
        f = _py(tmp_path, "dos_params.py", """
            def f1(host, port, otro): pass
            def f2(host, port, distinto): pass
        """)
        # host+port aparece en 2 funciones, pero el clump máximo es de 2 (< min_size=3)
        config = DesignReviewerConfig(min_data_clump_size=3, min_data_clump_occurrences=2)
        results = _ejecutar(DataClumpsAnalyzer(), f, config)

        assert results == []

    def test_no_detecta_una_sola_ocurrencia(self, tmp_path):
        """Grupo que aparece en solo 1 función no debe reportarse."""
        f = _py(tmp_path, "una_vez.py", """
            def sola(host, port, timeout): pass
            def otra(x, y, z): pass
        """)
        config = DesignReviewerConfig(min_data_clump_size=3, min_data_clump_occurrences=2)
        results = _ejecutar(DataClumpsAnalyzer(), f, config)

        assert results == []

    def test_reporta_solo_clumps_maximos(self, tmp_path):
        """Si {a,b,c,d} es un clump válido, no debe reportarse el sub-clump {a,b,c}."""
        f = _py(tmp_path, "maximo.py", """
            def f1(host, port, timeout, retries): pass
            def f2(host, port, timeout, retries): pass
        """)
        config = DesignReviewerConfig(min_data_clump_size=3, min_data_clump_occurrences=2)
        results = _ejecutar(DataClumpsAnalyzer(), f, config)

        # Solo debe reportarse el clump de 4, no los sub-clumps de 3
        assert len(results) == 1
        clump_params = set(results[0].message.split("{")[1].split("}")[0].split(", "))
        assert len(clump_params) == 4

    def test_detecta_multiples_clumps_independientes(self, tmp_path):
        """Dos grupos de parámetros distintos deben generar dos resultados."""
        f = _py(tmp_path, "dos_clumps.py", """
            def conectar(host, port, timeout): pass
            def reconectar(host, port, timeout): pass
            def registrar(nombre, apellido, edad): pass
            def actualizar(nombre, apellido, edad): pass
        """)
        config = DesignReviewerConfig(min_data_clump_size=3, min_data_clump_occurrences=2)
        results = _ejecutar(DataClumpsAnalyzer(), f, config)

        assert len(results) == 2
        smell_types = {r.smell_type for r in results}
        assert smell_types == {"DataClumps"}

    def test_mensaje_incluye_funciones_afectadas(self, tmp_path):
        """El mensaje debe listar los nombres de las funciones que comparten el clump."""
        f = _py(tmp_path, "funciones.py", """
            def inicio(host, port, timeout): pass
            def fin(host, port, timeout): pass
        """)
        config = DesignReviewerConfig(min_data_clump_size=3, min_data_clump_occurrences=2)
        results = _ejecutar(DataClumpsAnalyzer(), f, config)

        assert len(results) == 1
        assert "inicio" in results[0].message
        assert "fin" in results[0].message

    def test_archivo_con_error_de_sintaxis(self, tmp_path):
        """Archivo con error de sintaxis debe retornar lista vacía."""
        f = _py(tmp_path, "roto.py", "def roto(\n")
        results = _ejecutar(DataClumpsAnalyzer(), f, DesignReviewerConfig())

        assert results == []

    def test_umbrales_personalizados(self, tmp_path):
        """Debe respetar min_data_clump_size y min_data_clump_occurrences."""
        f = _py(tmp_path, "umbrales.py", """
            def f1(a, b, c, d): pass
            def f2(a, b, c, d): pass
            def f3(a, b, c, d): pass
        """)
        # Con size=4 y occurrences=2: {a,b,c,d} aparece 3 veces → detecta
        assert len(_ejecutar(DataClumpsAnalyzer(), f,
                             DesignReviewerConfig(min_data_clump_size=4,
                                                  min_data_clump_occurrences=2))) == 1
        # Con size=4 y occurrences=4: solo aparece 3 veces → no detecta
        assert len(_ejecutar(DataClumpsAnalyzer(), f,
                             DesignReviewerConfig(min_data_clump_size=4,
                                                  min_data_clump_occurrences=4))) == 0


# ─────────────────────────────────────────────────────────────────────────────
# Auto-discovery y metadatos
# ─────────────────────────────────────────────────────────────────────────────

class TestAutoDiscoverySmells:

    def test_orquestador_descubre_doce_analyzers(self):
        """El orquestador debe descubrir los 12 analyzers (7 previos + 5 smells)."""
        orch = AnalyzerOrchestrator(DesignReviewerConfig())

        nombres = {a.name for a in orch.analyzers}
        assert "GodObjectAnalyzer" in nombres
        assert "LongMethodAnalyzer" in nombres
        assert "LongParameterListAnalyzer" in nombres
        assert "FeatureEnvyAnalyzer" in nombres
        assert "DataClumpsAnalyzer" in nombres
        assert len(orch.analyzers) >= 12

    def test_smells_tienen_categoria_smells(self):
        """Los 5 analyzers de Fase 4 deben tener categoría 'smells'."""
        analyzers = [
            GodObjectAnalyzer(),
            LongMethodAnalyzer(),
            LongParameterListAnalyzer(),
            FeatureEnvyAnalyzer(),
            DataClumpsAnalyzer(),
        ]
        for a in analyzers:
            assert a.category == "smells", f"{a.name} tiene categoría '{a.category}', esperada 'smells'"

    def test_resultados_smells_tienen_solid_principle(self, tmp_path):
        """Los resultados de smells deben tener solid_principle distinto de None."""
        f = _py(tmp_path, "solid.py", """
            class Clase:
                def m1(self): pass
                def m2(self): pass
                def m3(self): pass
                def m4(self): pass
                def m5(self): pass
        """)
        config = DesignReviewerConfig(max_god_object_methods=3, max_god_object_lines=500)
        results = _ejecutar(GodObjectAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].solid_principle is not None
        assert isinstance(results[0].solid_principle, SolidPrinciple)

    def test_resultados_smells_tienen_smell_type(self, tmp_path):
        """Los resultados de smells deben tener smell_type distinto de None."""
        f = _py(tmp_path, "smelltype.py", """
            def funcion(a, b, c, d, e, f): pass
        """)
        config = DesignReviewerConfig(max_parameters=3)
        results = _ejecutar(LongParameterListAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].smell_type is not None
        assert results[0].smell_type == "LongParameterList"
