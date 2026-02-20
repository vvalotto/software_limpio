"""
Tests unitarios para los analyzers de cohesión y herencia de DesignReviewer.

Cubre LCOMAnalyzer, WMCAnalyzer, DITAnalyzer y NOPAnalyzer usando
fixtures de código Python sintético escritos inline con tmp_path.

Ticket: 3.6
"""

import textwrap
from pathlib import Path

import pytest

from quality_agents.designreviewer.analyzers.dit_analyzer import DITAnalyzer
from quality_agents.designreviewer.analyzers.lcom_analyzer import LCOMAnalyzer
from quality_agents.designreviewer.analyzers.nop_analyzer import NOPAnalyzer
from quality_agents.designreviewer.analyzers.wmc_analyzer import WMCAnalyzer
from quality_agents.designreviewer.config import DesignReviewerConfig
from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity
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
# LCOMAnalyzer
# ─────────────────────────────────────────────────────────────────────────────

class TestLCOMAnalyzer:

    def test_detecta_violacion_dos_grupos(self, tmp_path):
        """Clase con 2 grupos de métodos que no comparten atributos → LCOM=2."""
        f = _py(tmp_path, "dos_grupos.py", """
            class ClasePocoCohesiva:
                def leer_nombre(self):
                    return self.nombre

                def guardar_nombre(self, nombre):
                    self.nombre = nombre

                def calcular_precio(self):
                    return self.precio * self.cantidad

                def actualizar_precio(self, precio):
                    self.precio = precio
                    self.cantidad = 1
        """)
        config = DesignReviewerConfig(max_lcom=1)
        results = _ejecutar(LCOMAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.WARNING
        assert results[0].class_name == "ClasePocoCohesiva"
        assert results[0].current_value == 2

    def test_no_detecta_violacion_clase_cohesiva(self, tmp_path):
        """Clase cuyos métodos comparten atributos → LCOM=1 (cohesiva)."""
        f = _py(tmp_path, "cohesiva.py", """
            class Cohesiva:
                def __init__(self, valor):
                    self.valor = valor
                    self.activo = True

                def obtener(self):
                    return self.valor

                def activar(self):
                    self.activo = True
                    return self.valor

                def desactivar(self):
                    self.activo = False
        """)
        config = DesignReviewerConfig(max_lcom=1)
        results = _ejecutar(LCOMAnalyzer(), f, config)

        assert results == []

    def test_metodos_sin_atributos_se_excluyen(self, tmp_path):
        """Métodos que no acceden a self.X no participan en el cálculo de LCOM."""
        f = _py(tmp_path, "utility.py", """
            class ConUtilities:
                def calcular(self):
                    return self.valor * 2

                def actualizar(self, v):
                    self.valor = v

                def utilidad_pura(self, x, y):
                    return x + y

                def otra_utilidad(self, n):
                    return n * n
        """)
        config = DesignReviewerConfig(max_lcom=1)
        results = _ejecutar(LCOMAnalyzer(), f, config)

        # calcular y actualizar comparten self.valor → 1 componente → no viola
        assert results == []

    def test_no_detecta_solo_un_metodo_con_atributos(self, tmp_path):
        """Con 0 o 1 método que accede a self.X, no hay violación por definición."""
        f = _py(tmp_path, "un_metodo.py", """
            class ClasePequena:
                def iniciar(self):
                    self.estado = True

                def ayuda(self):
                    return 42
        """)
        config = DesignReviewerConfig(max_lcom=1)
        results = _ejecutar(LCOMAnalyzer(), f, config)

        assert results == []

    def test_estimated_effort_formula(self, tmp_path):
        """estimated_effort debe ser (lcom - umbral) * 1.5."""
        f = _py(tmp_path, "esfuerzo.py", """
            class TresGrupos:
                def a1(self): return self.a
                def a2(self): self.a = 1
                def b1(self): return self.b
                def b2(self): self.b = 2
                def c1(self): return self.c
                def c2(self): self.c = 3
        """)
        config = DesignReviewerConfig(max_lcom=1)
        results = _ejecutar(LCOMAnalyzer(), f, config)

        assert len(results) == 1
        lcom = results[0].current_value
        assert results[0].estimated_effort == round((lcom - 1) * 1.5, 1)

    def test_archivo_sin_clases(self, tmp_path):
        """Archivo sin clases debe retornar lista vacía."""
        f = _py(tmp_path, "sin_clases.py", """
            def funcion():
                return 42
        """)
        config = DesignReviewerConfig(max_lcom=1)
        results = _ejecutar(LCOMAnalyzer(), f, config)

        assert results == []

    def test_archivo_con_error_de_sintaxis(self, tmp_path):
        """Archivo con error de sintaxis debe retornar lista vacía sin lanzar."""
        f = _py(tmp_path, "roto.py", "def roto(\n")
        config = DesignReviewerConfig(max_lcom=1)
        results = _ejecutar(LCOMAnalyzer(), f, config)

        assert results == []

    def test_umbral_personalizado(self, tmp_path):
        """Debe respetar el umbral configurado."""
        f = _py(tmp_path, "umbral.py", """
            class DosGrupos:
                def a(self): return self.x
                def b(self): self.x = 1
                def c(self): return self.y
                def d(self): self.y = 2
        """)
        # LCOM=2: con umbral 1 viola, con umbral 2 no
        assert len(_ejecutar(LCOMAnalyzer(), f, DesignReviewerConfig(max_lcom=1))) == 1
        assert len(_ejecutar(LCOMAnalyzer(), f, DesignReviewerConfig(max_lcom=2))) == 0

    def test_staticmethod_excluido(self, tmp_path):
        """Los @staticmethod no deben participar en el cálculo de LCOM."""
        f = _py(tmp_path, "static.py", """
            class ConStatic:
                def real(self):
                    return self.valor

                def actualizar(self, v):
                    self.valor = v

                @staticmethod
                def helper(x):
                    return x * 2
        """)
        config = DesignReviewerConfig(max_lcom=1)
        results = _ejecutar(LCOMAnalyzer(), f, config)

        assert results == []


# ─────────────────────────────────────────────────────────────────────────────
# WMCAnalyzer
# ─────────────────────────────────────────────────────────────────────────────

class TestWMCAnalyzer:

    def test_detecta_violacion_wmc_alto(self, tmp_path):
        """Clase con métodos muy complejos cuya suma supera el umbral."""
        f = _py(tmp_path, "compleja.py", """
            class MuyCompleja:
                def m1(self, x, y, z):
                    if x > 0:
                        if y > 0:
                            if z > 0:
                                return x + y + z
                            return x + y
                        return x
                    return 0

                def m2(self, items):
                    resultado = []
                    for item in items:
                        if item > 0:
                            for sub in range(item):
                                if sub % 2 == 0:
                                    resultado.append(sub)
                    return resultado

                def m3(self, a, b, c, d):
                    if a and b:
                        return 1
                    elif a and c:
                        return 2
                    elif b and d:
                        return 3
                    elif c or d:
                        return 4
                    return 0

                def m4(self, n):
                    count = 0
                    while n > 0:
                        if n % 2 == 0:
                            n //= 2
                            count += 1
                        elif n % 3 == 0:
                            n //= 3
                        else:
                            n -= 1
                    return count

                def m5(self, data):
                    if not data:
                        return None
                    total = 0
                    for k, v in data.items():
                        if isinstance(v, int):
                            total += v
                        elif isinstance(v, list):
                            total += sum(v)
                    return total
        """)
        config = DesignReviewerConfig(max_wmc=20)
        results = _ejecutar(WMCAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.CRITICAL
        assert results[0].class_name == "MuyCompleja"
        assert results[0].current_value > 20

    def test_no_detecta_violacion_clase_simple(self, tmp_path):
        """Clase con métodos simples (CC=1 cada uno) no supera el umbral."""
        f = _py(tmp_path, "simple.py", """
            class Servicio:
                def obtener(self):
                    return self.valor

                def guardar(self, v):
                    self.valor = v

                def resetear(self):
                    self.valor = None
        """)
        config = DesignReviewerConfig(max_wmc=20)
        results = _ejecutar(WMCAnalyzer(), f, config)

        assert results == []

    def test_archivo_sin_clases(self, tmp_path):
        """Archivo con solo funciones no debe generar resultados."""
        f = _py(tmp_path, "funciones.py", """
            def funcion_a():
                return 1

            def funcion_b(x):
                if x:
                    return x
                return 0
        """)
        config = DesignReviewerConfig(max_wmc=20)
        results = _ejecutar(WMCAnalyzer(), f, config)

        assert results == []

    def test_estimated_effort_formula(self, tmp_path):
        """estimated_effort debe ser (wmc - umbral) * 0.3."""
        f = _py(tmp_path, "esfuerzo.py", """
            class Compleja:
                def m1(self, x, y, z):
                    if x > 0:
                        if y > 0:
                            if z > 0:
                                return x + y + z
                            return x + y
                        return x
                    return 0

                def m2(self, items):
                    resultado = []
                    for item in items:
                        if item > 0:
                            for sub in range(item):
                                if sub % 2 == 0:
                                    resultado.append(sub)
                    return resultado

                def m3(self, a, b, c, d):
                    if a and b:
                        return 1
                    elif a and c:
                        return 2
                    elif b and d:
                        return 3
                    elif c or d:
                        return 4
                    return 0

                def m4(self, n):
                    count = 0
                    while n > 0:
                        if n % 2 == 0:
                            n //= 2
                            count += 1
                        elif n % 3 == 0:
                            n //= 3
                        else:
                            n -= 1
                    return count

                def m5(self, data):
                    if not data:
                        return None
                    total = 0
                    for k, v in data.items():
                        if isinstance(v, int):
                            total += v
                        elif isinstance(v, list):
                            total += sum(v)
                    return total
        """)
        config = DesignReviewerConfig(max_wmc=20)
        results = _ejecutar(WMCAnalyzer(), f, config)

        assert len(results) == 1
        wmc = results[0].current_value
        exceso = wmc - 20
        assert results[0].estimated_effort == round(exceso * 0.3, 1)

    def test_archivo_con_error_de_sintaxis(self, tmp_path):
        """Archivo con error de sintaxis debe retornar lista vacía."""
        f = _py(tmp_path, "roto.py", "def roto(\n")
        config = DesignReviewerConfig(max_wmc=20)
        results = _ejecutar(WMCAnalyzer(), f, config)

        assert results == []

    def test_umbral_personalizado(self, tmp_path):
        """Debe respetar el umbral configurado."""
        f = _py(tmp_path, "umbral.py", """
            class Clase:
                def m1(self, x):
                    if x > 0:
                        if x > 10:
                            return x * 2
                        return x
                    return 0

                def m2(self, y):
                    if y:
                        return y + 1
                    return 0
        """)
        # WMC = CC(m1)=3 + CC(m2)=2 = 5
        assert len(_ejecutar(WMCAnalyzer(), f, DesignReviewerConfig(max_wmc=4))) == 1
        assert len(_ejecutar(WMCAnalyzer(), f, DesignReviewerConfig(max_wmc=20))) == 0

    def test_multiples_clases_detecta_solo_la_violacion(self, tmp_path):
        """Con dos clases, solo debe reportar la que supera el umbral."""
        f = _py(tmp_path, "mixta.py", """
            class Simple:
                def uno(self): return 1
                def dos(self): return 2

            class Compleja:
                def m1(self, x, y, z):
                    if x > 0:
                        if y > 0:
                            if z > 0: return x + y + z
                            return x + y
                        return x
                    return 0
                def m2(self, items):
                    for item in items:
                        if item > 0:
                            for sub in range(item):
                                if sub % 2 == 0:
                                    yield sub
                def m3(self, a, b, c):
                    if a and b: return 1
                    elif a and c: return 2
                    elif b or c: return 3
                    return 0
                def m4(self, n):
                    count = 0
                    while n > 0:
                        if n % 2 == 0: n //= 2; count += 1
                        elif n % 3 == 0: n //= 3
                        else: n -= 1
                    return count
                def m5(self, d):
                    if not d: return None
                    for k, v in d.items():
                        if isinstance(v, int): yield v
                        elif isinstance(v, list): yield from v
        """)
        config = DesignReviewerConfig(max_wmc=20)
        results = _ejecutar(WMCAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].class_name == "Compleja"


# ─────────────────────────────────────────────────────────────────────────────
# DITAnalyzer
# ─────────────────────────────────────────────────────────────────────────────

class TestDITAnalyzer:

    def test_detecta_violacion_herencia_profunda(self, tmp_path):
        """Cadena A→B→C→D→E→F tiene DIT=6, supera el umbral de 5."""
        f = _py(tmp_path, "profunda.py", """
            class A:
                pass
            class B(A):
                pass
            class C(B):
                pass
            class D(C):
                pass
            class E(D):
                pass
            class F(E):
                pass
        """)
        config = DesignReviewerConfig(max_dit=5)
        results = _ejecutar(DITAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.CRITICAL
        assert results[0].class_name == "F"
        assert results[0].current_value == 6

    def test_no_detecta_herencia_simple(self, tmp_path):
        """Cadena de 2 niveles no supera el umbral."""
        f = _py(tmp_path, "simple.py", """
            class Base:
                pass
            class Hijo(Base):
                pass
        """)
        config = DesignReviewerConfig(max_dit=5)
        results = _ejecutar(DITAnalyzer(), f, config)

        assert results == []

    def test_clase_sin_bases_tiene_dit_uno(self, tmp_path):
        """Clase sin bases explícitas tiene DIT=1 (hereda de object)."""
        f = _py(tmp_path, "sin_bases.py", """
            class SinBases:
                pass
        """)
        config = DesignReviewerConfig(max_dit=5)
        a = DITAnalyzer()
        ctx = ExecutionContext(file_path=f, config=config)
        a.should_run(ctx)

        import ast
        tree = ast.parse(f.read_text())
        clases = a._extraer_clases(tree)
        memo: dict = {}
        dit = a._calcular_dit("SinBases", clases, memo, set())

        assert dit == 1

    def test_clase_con_base_externa_tiene_dit_dos(self, tmp_path):
        """Clase que hereda de una clase externa tiene DIT=2 (externa=1, +1)."""
        f = _py(tmp_path, "externa.py", """
            class Hijo(ClaseExterna):
                pass
        """)
        config = DesignReviewerConfig(max_dit=5)
        a = DITAnalyzer()
        ctx = ExecutionContext(file_path=f, config=config)
        a.should_run(ctx)

        import ast
        tree = ast.parse(f.read_text())
        clases = a._extraer_clases(tree)
        memo: dict = {}
        dit = a._calcular_dit("Hijo", clases, memo, set())

        assert dit == 2

    def test_herencia_multiple_toma_maximo(self, tmp_path):
        """Con herencia múltiple, DIT toma el máximo de las bases."""
        f = _py(tmp_path, "multiple.py", """
            class A:
                pass
            class B(A):
                pass
            class C(A):
                pass
            class D(B, C):
                pass
        """)
        config = DesignReviewerConfig(max_dit=5)
        a = DITAnalyzer()
        ctx = ExecutionContext(file_path=f, config=config)
        a.should_run(ctx)

        import ast
        tree = ast.parse(f.read_text())
        clases = a._extraer_clases(tree)
        memo: dict = {}
        # DIT(A)=1, DIT(B)=2, DIT(C)=2, DIT(D)=max(2,2)+1=3
        assert a._calcular_dit("D", clases, memo, set()) == 3

    def test_no_detecta_archivo_sin_clases(self, tmp_path):
        """Archivo sin clases debe retornar lista vacía."""
        f = _py(tmp_path, "sin_clases.py", "x = 1\n")
        config = DesignReviewerConfig(max_dit=5)
        results = _ejecutar(DITAnalyzer(), f, config)

        assert results == []

    def test_archivo_con_error_de_sintaxis(self, tmp_path):
        """Archivo con error de sintaxis debe retornar lista vacía."""
        f = _py(tmp_path, "roto.py", "def roto(\n")
        config = DesignReviewerConfig(max_dit=5)
        results = _ejecutar(DITAnalyzer(), f, config)

        assert results == []

    def test_estimated_effort_formula(self, tmp_path):
        """estimated_effort debe ser (dit - umbral) * 2.0."""
        f = _py(tmp_path, "esfuerzo.py", """
            class A:
                pass
            class B(A):
                pass
            class C(B):
                pass
            class D(C):
                pass
            class E(D):
                pass
            class F(E):
                pass
        """)
        config = DesignReviewerConfig(max_dit=5)
        results = _ejecutar(DITAnalyzer(), f, config)

        assert len(results) == 1
        dit = results[0].current_value
        assert results[0].estimated_effort == round((dit - 5) * 2.0, 1)

    def test_umbral_personalizado(self, tmp_path):
        """Debe respetar el umbral configurado."""
        f = _py(tmp_path, "umbral.py", """
            class A:
                pass
            class B(A):
                pass
            class C(B):
                pass
        """)
        # DIT(C) = 3: viola umbral 2, no viola umbral 5
        assert len(_ejecutar(DITAnalyzer(), f, DesignReviewerConfig(max_dit=2))) == 1
        assert len(_ejecutar(DITAnalyzer(), f, DesignReviewerConfig(max_dit=5))) == 0


# ─────────────────────────────────────────────────────────────────────────────
# NOPAnalyzer
# ─────────────────────────────────────────────────────────────────────────────

class TestNOPAnalyzer:

    def test_detecta_violacion_herencia_multiple(self, tmp_path):
        """Clase con 3 padres directos viola umbral de 1."""
        f = _py(tmp_path, "multiple.py", """
            class MultiPadre(BaseA, MixinB, MixinC):
                pass
        """)
        config = DesignReviewerConfig(max_nop=1)
        results = _ejecutar(NOPAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.CRITICAL
        assert results[0].class_name == "MultiPadre"
        assert results[0].current_value == 3

    def test_no_detecta_herencia_simple(self, tmp_path):
        """Clase con un solo padre no viola el umbral."""
        f = _py(tmp_path, "simple.py", """
            class Hijo(Padre):
                pass
        """)
        config = DesignReviewerConfig(max_nop=1)
        results = _ejecutar(NOPAnalyzer(), f, config)

        assert results == []

    def test_no_detecta_clase_sin_bases(self, tmp_path):
        """Clase sin bases explícitas tiene NOP=0, no viola."""
        f = _py(tmp_path, "sin_bases.py", """
            class SinBases:
                pass
        """)
        config = DesignReviewerConfig(max_nop=1)
        results = _ejecutar(NOPAnalyzer(), f, config)

        assert results == []

    def test_excluye_object(self, tmp_path):
        """`object` explícito no debe contar como padre."""
        f = _py(tmp_path, "object_explicito.py", """
            class ConObject(object):
                pass
        """)
        config = DesignReviewerConfig(max_nop=1)
        results = _ejecutar(NOPAnalyzer(), f, config)

        assert results == []

    def test_excluye_abc(self, tmp_path):
        """`ABC` solo no debe generar violación."""
        f = _py(tmp_path, "solo_abc.py", """
            from abc import ABC
            class MiAbstracta(ABC):
                pass
        """)
        config = DesignReviewerConfig(max_nop=1)
        results = _ejecutar(NOPAnalyzer(), f, config)

        assert results == []

    def test_abc_mas_mixin_cuenta_mixins(self, tmp_path):
        """ABC se excluye pero los mixins adicionales sí cuentan."""
        f = _py(tmp_path, "abc_mixins.py", """
            class ConMixins(ABC, MixinX, MixinY):
                pass
        """)
        config = DesignReviewerConfig(max_nop=1)
        results = _ejecutar(NOPAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].current_value == 2  # MixinX + MixinY (ABC excluido)

    def test_mensaje_incluye_nombres_de_padres(self, tmp_path):
        """El mensaje debe listar los nombres de los padres problemáticos."""
        f = _py(tmp_path, "info.py", """
            class Hijo(BaseAlfa, BaseBeta, BaseGamma):
                pass
        """)
        config = DesignReviewerConfig(max_nop=1)
        results = _ejecutar(NOPAnalyzer(), f, config)

        assert len(results) == 1
        assert "BaseAlfa" in results[0].message
        assert "BaseBeta" in results[0].message
        assert "BaseGamma" in results[0].message

    def test_estimated_effort_formula(self, tmp_path):
        """estimated_effort debe ser (nop - umbral) * 1.0."""
        f = _py(tmp_path, "esfuerzo.py", """
            class Hijo(A, B, C, D):
                pass
        """)
        config = DesignReviewerConfig(max_nop=1)
        results = _ejecutar(NOPAnalyzer(), f, config)

        assert len(results) == 1
        nop = results[0].current_value
        assert results[0].estimated_effort == round((nop - 1) * 1.0, 1)

    def test_archivo_con_error_de_sintaxis(self, tmp_path):
        """Archivo con error de sintaxis debe retornar lista vacía."""
        f = _py(tmp_path, "roto.py", "def roto(\n")
        config = DesignReviewerConfig(max_nop=1)
        results = _ejecutar(NOPAnalyzer(), f, config)

        assert results == []

    def test_umbral_personalizado(self, tmp_path):
        """Debe respetar el umbral configurado."""
        f = _py(tmp_path, "umbral.py", """
            class Hijo(A, B):
                pass
        """)
        # NOP=2: viola umbral 1, no viola umbral 2
        assert len(_ejecutar(NOPAnalyzer(), f, DesignReviewerConfig(max_nop=1))) == 1
        assert len(_ejecutar(NOPAnalyzer(), f, DesignReviewerConfig(max_nop=2))) == 0


# ─────────────────────────────────────────────────────────────────────────────
# Auto-discovery
# ─────────────────────────────────────────────────────────────────────────────

class TestAutoDiscoveryCohesionHerencia:

    def test_orquestador_descubre_siete_analyzers(self):
        """El orquestador debe descubrir los 7 analyzers (3 acoplamiento + 4 cohesión/herencia)."""
        orch = AnalyzerOrchestrator(DesignReviewerConfig())

        nombres = {a.name for a in orch.analyzers}
        assert "LCOMAnalyzer" in nombres
        assert "WMCAnalyzer" in nombres
        assert "DITAnalyzer" in nombres
        assert "NOPAnalyzer" in nombres
        assert len(orch.analyzers) == 7

    def test_lcom_categoria_cohesion(self):
        """LCOMAnalyzer debe tener categoría 'cohesion'."""
        assert LCOMAnalyzer().category == "cohesion"

    def test_wmc_categoria_cohesion(self):
        """WMCAnalyzer debe tener categoría 'cohesion'."""
        assert WMCAnalyzer().category == "cohesion"

    def test_dit_categoria_inheritance(self):
        """DITAnalyzer debe tener categoría 'inheritance'."""
        assert DITAnalyzer().category == "inheritance"

    def test_nop_categoria_inheritance(self):
        """NOPAnalyzer debe tener categoría 'inheritance'."""
        assert NOPAnalyzer().category == "inheritance"
