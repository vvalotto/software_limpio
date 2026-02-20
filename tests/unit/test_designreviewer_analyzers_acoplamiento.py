"""
Tests unitarios para los analyzers de acoplamiento de DesignReviewer.

Cubre CBOAnalyzer, FanOutAnalyzer y CircularImportsAnalyzer usando
fixtures de código Python sintético escritos inline con tmp_path.

Ticket: 2.5
"""

import textwrap
from pathlib import Path

import pytest

from quality_agents.designreviewer.analyzers.cbo_analyzer import CBOAnalyzer
from quality_agents.designreviewer.analyzers.circular_imports_analyzer import (
    CircularImportsAnalyzer,
)
from quality_agents.designreviewer.analyzers.fan_out_analyzer import FanOutAnalyzer
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
# CBOAnalyzer
# ─────────────────────────────────────────────────────────────────────────────

class TestCBOAnalyzer:

    def test_detecta_violacion_por_type_hints(self, tmp_path):
        """Debe detectar CBO alto cuando la clase tiene muchos type hints externos."""
        f = _py(tmp_path, "alto.py", """
            class ServicioAlto:
                def __init__(
                    self,
                    repo: RepositorioA,
                    cache: CacheB,
                    logger: LoggerC,
                    notif: NotificadorD,
                    validator: ValidadorE,
                    mapper: MapperF,
                ):
                    pass
        """)
        config = DesignReviewerConfig(max_cbo=5)
        results = _ejecutar(CBOAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.CRITICAL
        assert results[0].class_name == "ServicioAlto"
        assert results[0].current_value >= 6

    def test_detecta_violacion_por_instanciaciones(self, tmp_path):
        """Debe detectar CBO alto cuando la clase instancia muchas clases externas."""
        f = _py(tmp_path, "instancias.py", """
            class ServicioInstancias:
                def __init__(self):
                    self.a = ClaseA()
                    self.b = ClaseB()
                    self.c = ClaseC()
                    self.d = ClaseD()
                    self.e = ClaseE()
                    self.f = ClaseF()
        """)
        config = DesignReviewerConfig(max_cbo=5)
        results = _ejecutar(CBOAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].current_value >= 6

    def test_detecta_violacion_por_herencia(self, tmp_path):
        """Las clases base deben contar como acoplamiento."""
        f = _py(tmp_path, "herencia.py", """
            class Hijo(BaseA, MixinB, MixinC, MixinD, MixinE, MixinF):
                pass
        """)
        config = DesignReviewerConfig(max_cbo=5)
        results = _ejecutar(CBOAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].current_value >= 6

    def test_no_detecta_violacion_clase_limpia(self, tmp_path):
        """Clase con pocas dependencias no debe generar resultados."""
        f = _py(tmp_path, "limpio.py", """
            class ServicioLimpio:
                def __init__(self, repo: Repositorio):
                    self.repo = repo
                    self.logger = Logger()
        """)
        config = DesignReviewerConfig(max_cbo=5)
        results = _ejecutar(CBOAnalyzer(), f, config)

        assert results == []

    def test_ignora_tipos_builtin(self, tmp_path):
        """Los tipos built-in de Python no deben contar como acoplamiento."""
        f = _py(tmp_path, "builtins.py", """
            class Procesador:
                def procesar(
                    self,
                    datos: list,
                    config: dict,
                    nombre: str,
                    activo: bool,
                    cantidad: int,
                    valor: float,
                ) -> None:
                    pass
        """)
        config = DesignReviewerConfig(max_cbo=5)
        results = _ejecutar(CBOAnalyzer(), f, config)

        assert results == []

    def test_archivo_sin_clases(self, tmp_path):
        """Archivo sin clases debe retornar lista vacía."""
        f = _py(tmp_path, "sin_clases.py", """
            def funcion():
                return 42

            CONSTANTE = "valor"
        """)
        config = DesignReviewerConfig(max_cbo=5)
        results = _ejecutar(CBOAnalyzer(), f, config)

        assert results == []

    def test_resultado_contiene_clases_acopladas(self, tmp_path):
        """El mensaje debe incluir los nombres de las clases acopladas."""
        f = _py(tmp_path, "info.py", """
            class MiServicio:
                def __init__(self):
                    self.a = ClaseAlfa()
                    self.b = ClaseBeta()
                    self.c = ClaseGamma()
                    self.d = ClaseDelta()
                    self.e = ClaseEpsilon()
                    self.f = ClaseZeta()
        """)
        config = DesignReviewerConfig(max_cbo=5)
        results = _ejecutar(CBOAnalyzer(), f, config)

        assert len(results) == 1
        assert "ClaseAlfa" in results[0].message or "ClaseBeta" in results[0].message

    def test_estimated_effort_formula(self, tmp_path):
        """estimated_effort debe ser (cbo - umbral) * 0.5."""
        f = _py(tmp_path, "esfuerzo.py", """
            class Clase:
                def __init__(self):
                    self.a = A()
                    self.b = B()
                    self.c = C()
                    self.d = D()
                    self.e = E()
                    self.f = F()
                    self.g = G()
        """)
        config = DesignReviewerConfig(max_cbo=5)
        results = _ejecutar(CBOAnalyzer(), f, config)

        assert len(results) == 1
        cbo = results[0].current_value
        exceso = cbo - 5
        assert results[0].estimated_effort == round(exceso * 0.5, 1)

    def test_archivo_con_error_de_sintaxis(self, tmp_path):
        """Un archivo con error de sintaxis debe retornar lista vacía sin lanzar."""
        f = _py(tmp_path, "roto.py", "def roto(\n")
        config = DesignReviewerConfig(max_cbo=5)
        results = _ejecutar(CBOAnalyzer(), f, config)

        assert results == []

    def test_umbral_personalizado(self, tmp_path):
        """Debe respetar el umbral configurado."""
        f = _py(tmp_path, "umbral.py", """
            class MiClase:
                def __init__(self):
                    self.a = A()
                    self.b = B()
                    self.c = C()
        """)
        # Con umbral 2 debe detectar violación, con umbral 5 no
        assert len(_ejecutar(CBOAnalyzer(), f, DesignReviewerConfig(max_cbo=2))) == 1
        assert len(_ejecutar(CBOAnalyzer(), f, DesignReviewerConfig(max_cbo=5))) == 0


# ─────────────────────────────────────────────────────────────────────────────
# FanOutAnalyzer
# ─────────────────────────────────────────────────────────────────────────────

class TestFanOutAnalyzer:

    def test_detecta_violacion_muchos_imports(self, tmp_path):
        """Debe detectar Fan-Out alto con muchos imports externos."""
        f = _py(tmp_path, "alto.py", """
            import os
            import sys
            import json
            import logging
            import pathlib
            import datetime
            import collections
            import itertools
        """)
        config = DesignReviewerConfig(max_fan_out=7)
        results = _ejecutar(FanOutAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.WARNING
        assert results[0].current_value == 8

    def test_detecta_violacion_from_imports(self, tmp_path):
        """Debe contar módulos de `from X import Y` también."""
        f = _py(tmp_path, "from_imports.py", """
            from os import path
            from sys import argv
            from json import dumps
            from logging import getLogger
            from pathlib import Path
            from datetime import datetime
            from collections import defaultdict
            from itertools import chain
        """)
        config = DesignReviewerConfig(max_fan_out=7)
        results = _ejecutar(FanOutAnalyzer(), f, config)

        assert len(results) == 1
        assert results[0].current_value == 8

    def test_no_detecta_violacion_pocos_imports(self, tmp_path):
        """Archivo con pocos imports no debe generar resultados."""
        f = _py(tmp_path, "limpio.py", """
            import os
            from pathlib import Path
            from typing import List
        """)
        config = DesignReviewerConfig(max_fan_out=7)
        results = _ejecutar(FanOutAnalyzer(), f, config)

        assert results == []

    def test_ignora_imports_relativos(self, tmp_path):
        """Los imports relativos no deben contar como Fan-Out."""
        f = _py(tmp_path, "relativo.py", """
            from . import hermano
            from .modulo import algo
            from ..paquete import otra_cosa
            import os
        """)
        config = DesignReviewerConfig(max_fan_out=7)
        results = _ejecutar(FanOutAnalyzer(), f, config)

        # Solo 'os' cuenta como externo
        assert results == []

    def test_cuenta_modulo_raiz_unico(self, tmp_path):
        """Múltiples imports del mismo paquete raíz deben contar como uno solo."""
        f = _py(tmp_path, "mismo_raiz.py", """
            from os import path
            from os.path import join
            import os
        """)
        config = DesignReviewerConfig(max_fan_out=7)
        results = _ejecutar(FanOutAnalyzer(), f, config)

        # 'os', 'os.path', 'os' → solo 1 módulo raíz único
        assert results == []

    def test_archivo_vacio(self, tmp_path):
        """Archivo vacío debe retornar lista vacía."""
        f = _py(tmp_path, "vacio.py", "")
        config = DesignReviewerConfig(max_fan_out=7)
        results = _ejecutar(FanOutAnalyzer(), f, config)

        assert results == []

    def test_estimated_effort_formula(self, tmp_path):
        """estimated_effort debe ser (fan_out - umbral) * 0.25."""
        f = _py(tmp_path, "esfuerzo.py", """
            import os
            import sys
            import json
            import logging
            import pathlib
            import datetime
            import collections
            import itertools
            import functools
        """)
        config = DesignReviewerConfig(max_fan_out=7)
        results = _ejecutar(FanOutAnalyzer(), f, config)

        assert len(results) == 1
        fan_out = results[0].current_value
        exceso = fan_out - 7
        assert results[0].estimated_effort == round(exceso * 0.25, 1)

    def test_umbral_personalizado(self, tmp_path):
        """Debe respetar el umbral configurado."""
        f = _py(tmp_path, "umbral.py", """
            import os
            import sys
            import json
        """)
        assert len(_ejecutar(FanOutAnalyzer(), f, DesignReviewerConfig(max_fan_out=2))) == 1
        assert len(_ejecutar(FanOutAnalyzer(), f, DesignReviewerConfig(max_fan_out=7))) == 0


# ─────────────────────────────────────────────────────────────────────────────
# CircularImportsAnalyzer
# ─────────────────────────────────────────────────────────────────────────────

class TestCircularImportsAnalyzer:

    def test_detecta_ciclo_directo(self, tmp_path):
        """Debe detectar ciclo cuando A importa B y B importa A."""
        _py(tmp_path, "a.py", "from b import algo\n")
        _py(tmp_path, "b.py", "from a import otra_cosa\n")

        config = DesignReviewerConfig()
        results = _ejecutar(CircularImportsAnalyzer(), tmp_path / "a.py", config)

        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.CRITICAL
        assert "b.py" in results[0].message

    def test_detecta_ciclo_con_import_simple(self, tmp_path):
        """Debe detectar ciclo con `import X` además de `from X import Y`."""
        _py(tmp_path, "modulo1.py", "import modulo2\n")
        _py(tmp_path, "modulo2.py", "import modulo1\n")

        config = DesignReviewerConfig()
        results = _ejecutar(CircularImportsAnalyzer(), tmp_path / "modulo1.py", config)

        assert len(results) == 1

    def test_no_detecta_ciclo_sin_retorno(self, tmp_path):
        """Si A importa B pero B no importa A, no hay ciclo."""
        _py(tmp_path, "a.py", "from b import algo\n")
        _py(tmp_path, "b.py", "import os\n")

        config = DesignReviewerConfig()
        results = _ejecutar(CircularImportsAnalyzer(), tmp_path / "a.py", config)

        assert results == []

    def test_no_detecta_ciclo_sin_imports(self, tmp_path):
        """Archivo sin imports no puede tener ciclos."""
        _py(tmp_path, "sin_imports.py", "x = 1\n")

        config = DesignReviewerConfig()
        results = _ejecutar(CircularImportsAnalyzer(), tmp_path / "sin_imports.py", config)

        assert results == []

    def test_ignora_imports_relativos(self, tmp_path):
        """Los imports relativos no deben considerarse para ciclos."""
        _py(tmp_path, "a.py", "from . import b\n")
        _py(tmp_path, "b.py", "from . import a\n")

        config = DesignReviewerConfig()
        results = _ejecutar(CircularImportsAnalyzer(), tmp_path / "a.py", config)

        # Los imports relativos se ignoran, no se detecta ciclo
        assert results == []

    def test_estimated_effort_fijo(self, tmp_path):
        """El estimated_effort de un ciclo debe ser siempre 2.0 horas."""
        _py(tmp_path, "x.py", "from y import Z\n")
        _py(tmp_path, "y.py", "from x import W\n")

        config = DesignReviewerConfig()
        results = _ejecutar(CircularImportsAnalyzer(), tmp_path / "x.py", config)

        assert len(results) == 1
        assert results[0].estimated_effort == 2.0

    def test_mensaje_incluye_archivos_involucrados(self, tmp_path):
        """El mensaje debe identificar ambos archivos del ciclo."""
        _py(tmp_path, "servicio.py", "from repositorio import Repo\n")
        _py(tmp_path, "repositorio.py", "from servicio import Servicio\n")

        config = DesignReviewerConfig()
        results = _ejecutar(
            CircularImportsAnalyzer(), tmp_path / "servicio.py", config
        )

        assert len(results) == 1
        assert "repositorio.py" in results[0].message

    def test_archivo_con_error_de_sintaxis(self, tmp_path):
        """Archivo con error de sintaxis debe retornar lista vacía sin lanzar."""
        _py(tmp_path, "roto.py", "def roto(\n")

        config = DesignReviewerConfig()
        results = _ejecutar(CircularImportsAnalyzer(), tmp_path / "roto.py", config)

        assert results == []


# ─────────────────────────────────────────────────────────────────────────────
# Auto-discovery
# ─────────────────────────────────────────────────────────────────────────────

class TestAutoDiscovery:

    def test_orquestador_descubre_analyzers_de_acoplamiento(self):
        """El orquestador debe descubrir los 3 analyzers de acoplamiento entre los disponibles."""
        orch = AnalyzerOrchestrator(DesignReviewerConfig())

        nombres = {a.name for a in orch.analyzers}
        assert "CBOAnalyzer" in nombres
        assert "FanOutAnalyzer" in nombres
        assert "CircularImportsAnalyzer" in nombres
