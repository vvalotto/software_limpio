"""
Tests unitarios para RefusedBequestAnalyzer (LSP).

Ticket: Issue #72
"""

import textwrap
from pathlib import Path

from quality_agents.designreviewer.analyzers.refused_bequest_analyzer import (
    RefusedBequestAnalyzer,
)
from quality_agents.designreviewer.config import DesignReviewerChecksConfig, DesignReviewerConfig
from quality_agents.designreviewer.models import SolidPrinciple
from quality_agents.shared.verifiable import ExecutionContext


def _py(tmp_path: Path, nombre: str, codigo: str) -> Path:
    archivo = tmp_path / nombre
    archivo.write_text(textwrap.dedent(codigo))
    return archivo


def _ejecutar(analyzer, archivo: Path, config: DesignReviewerConfig):
    ctx = ExecutionContext(file_path=archivo, config=config)
    analyzer.should_run(ctx)
    return analyzer.execute(archivo)


class TestRefusedBequestAnalyzer:
    def test_detecta_metodo_vaciado_con_pass(self, tmp_path):
        f = _py(tmp_path, "vaciado.py", """
            class Ave:
                def volar(self):
                    self.altura += 100
                    return self.altura

            class Pinguino(Ave):
                def volar(self):
                    pass
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())

        assert len(resultados) == 1
        r = resultados[0]
        assert r.class_name == "Pinguino"
        assert r.solid_principle == SolidPrinciple.LSP
        assert r.smell_type == "RefusedBequest"

    def test_detecta_metodo_vaciado_con_ellipsis(self, tmp_path):
        f = _py(tmp_path, "elipsis.py", """
            class Ave:
                def volar(self):
                    self.altura += 100
                    return self.altura

            class Pinguino(Ave):
                def volar(self):
                    ...
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())
        assert len(resultados) == 1

    def test_detecta_metodo_con_raise_not_implemented(self, tmp_path):
        f = _py(tmp_path, "raise_ni.py", """
            class Ave:
                def volar(self):
                    self.altura += 100
                    return self.altura

            class Pinguino(Ave):
                def volar(self):
                    raise NotImplementedError("los pingüinos no vuelan")
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())
        assert len(resultados) == 1

    def test_docstring_no_cuenta_como_implementacion(self, tmp_path):
        """pass precedido de docstring sigue siendo trivial."""
        f = _py(tmp_path, "docstring.py", """
            class Ave:
                def volar(self):
                    self.altura += 100
                    return self.altura

            class Pinguino(Ave):
                def volar(self):
                    '''Los pingüinos no vuelan.'''
                    pass
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())
        assert len(resultados) == 1

    def test_no_reporta_si_subclase_implementa_de_verdad(self, tmp_path):
        f = _py(tmp_path, "implementa.py", """
            class Ave:
                def volar(self):
                    self.altura += 100
                    return self.altura

            class Aguila(Ave):
                def volar(self):
                    self.altura += 500
                    return self.altura
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_no_reporta_si_base_tambien_es_trivial(self, tmp_path):
        """Si el método base ya es trivial (ej: template abstracto informal), no hay refuse."""
        f = _py(tmp_path, "base_trivial.py", """
            class Ave:
                def volar(self):
                    pass

            class Pinguino(Ave):
                def volar(self):
                    pass
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_excluye_metodos_dunder(self, tmp_path):
        f = _py(tmp_path, "dunder.py", """
            class Base:
                def __init__(self):
                    self.x = 1
                    self.y = 2

            class Derivada(Base):
                def __init__(self):
                    pass
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_excluye_metodo_decorado_con_abstractmethod(self, tmp_path):
        f = _py(tmp_path, "abstracto.py", """
            from abc import abstractmethod

            class Base:
                def procesar(self):
                    return self.calcular() + 1

            class Intermedia(Base):
                @abstractmethod
                def procesar(self):
                    pass
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_excluye_clase_que_hereda_de_abc(self, tmp_path):
        f = _py(tmp_path, "hereda_abc.py", """
            from abc import ABC

            class Base:
                def procesar(self):
                    return self.calcular() + 1

            class Intermedia(Base, ABC):
                def procesar(self):
                    pass
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_excluye_base_que_hereda_de_protocol(self, tmp_path):
        f = _py(tmp_path, "base_protocol.py", """
            from typing import Protocol

            class Contrato(Protocol):
                def procesar(self):
                    return self.calcular() + 1

            class Impl(Contrato):
                def procesar(self):
                    pass
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_excluye_clase_con_metaclass_abcmeta(self, tmp_path):
        f = _py(tmp_path, "metaclass_abc.py", """
            from abc import ABCMeta

            class Base:
                def procesar(self):
                    return self.calcular() + 1

            class Intermedia(Base, metaclass=ABCMeta):
                def procesar(self):
                    pass
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_ignora_base_externa_no_definida_en_el_archivo(self, tmp_path):
        f = _py(tmp_path, "base_externa.py", """
            import unittest

            class MiTest(unittest.TestCase):
                def setUp(self):
                    pass
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_no_reporta_metodo_nuevo_sin_override(self, tmp_path):
        f = _py(tmp_path, "sin_override.py", """
            class Ave:
                def volar(self):
                    self.altura += 100
                    return self.altura

            class Pinguino(Ave):
                def nadar(self):
                    pass
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_deshabilitado_por_config_no_ejecuta(self, tmp_path):
        f = _py(tmp_path, "vaciado2.py", """
            class Ave:
                def volar(self):
                    self.altura += 100
                    return self.altura

            class Pinguino(Ave):
                def volar(self):
                    pass
        """)
        config = DesignReviewerConfig(checks=DesignReviewerChecksConfig(refused_bequest=False))
        analyzer = RefusedBequestAnalyzer()
        ctx = ExecutionContext(file_path=f, config=config)
        assert analyzer.should_run(ctx) is False

    def test_archivo_sin_clases_no_falla(self, tmp_path):
        f = _py(tmp_path, "sin_clases.py", """
            def funcion():
                return 42
        """)
        resultados = _ejecutar(RefusedBequestAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []
