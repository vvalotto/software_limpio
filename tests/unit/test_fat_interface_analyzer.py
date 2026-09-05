"""
Tests unitarios para FatInterfaceAnalyzer (ISP).

Ticket: Issue #73
"""

import textwrap
from pathlib import Path

from quality_agents.designreviewer.analyzers.fat_interface_analyzer import FatInterfaceAnalyzer
from quality_agents.designreviewer.config import DesignReviewerChecksConfig, DesignReviewerConfig
from quality_agents.designreviewer.models import ReviewSeverity, SolidPrinciple
from quality_agents.shared.verifiable import ExecutionContext


def _py(tmp_path: Path, nombre: str, codigo: str) -> Path:
    archivo = tmp_path / nombre
    archivo.write_text(textwrap.dedent(codigo))
    return archivo


def _ejecutar(analyzer, archivo: Path, config: DesignReviewerConfig):
    ctx = ExecutionContext(file_path=archivo, config=config)
    analyzer.should_run(ctx)
    return analyzer.execute(archivo)


def _metodos_abc(n: int) -> str:
    return "\n".join(
        f"    @abstractmethod\n    def metodo_{i}(self): ..." for i in range(n)
    )


def _metodos_protocol(n: int) -> str:
    return "\n".join(f"    def metodo_{i}(self): ..." for i in range(n))


class TestFatInterfaceAnalyzer:
    def test_no_reporta_abc_con_pocos_metodos(self, tmp_path):
        codigo = "from abc import ABC, abstractmethod\n\nclass Interfaz(ABC):\n" + _metodos_abc(3)
        f = _py(tmp_path, "abc_chica.py", codigo)
        resultados = _ejecutar(FatInterfaceAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_reporta_abc_con_muchos_metodos_como_warning(self, tmp_path):
        codigo = "from abc import ABC, abstractmethod\n\nclass Interfaz(ABC):\n" + _metodos_abc(6)
        f = _py(tmp_path, "abc_gorda.py", codigo)
        resultados = _ejecutar(FatInterfaceAnalyzer(), f, DesignReviewerConfig())

        assert len(resultados) == 1
        r = resultados[0]
        assert r.class_name == "Interfaz"
        assert r.severity == ReviewSeverity.WARNING
        assert r.current_value == 6
        assert r.threshold == 5
        assert r.solid_principle == SolidPrinciple.ISP
        assert r.smell_type == "FatInterface"

    def test_reporta_abc_muy_gorda_como_critical(self, tmp_path):
        """Más del doble del umbral (>10) → CRITICAL."""
        codigo = "from abc import ABC, abstractmethod\n\nclass Interfaz(ABC):\n" + _metodos_abc(11)
        f = _py(tmp_path, "abc_muy_gorda.py", codigo)
        resultados = _ejecutar(FatInterfaceAnalyzer(), f, DesignReviewerConfig())

        assert len(resultados) == 1
        assert resultados[0].severity == ReviewSeverity.CRITICAL

    def test_no_cuenta_metodos_concretos_en_abc(self, tmp_path):
        """En ABC solo cuentan los @abstractmethod, no los métodos concretos."""
        codigo = textwrap.dedent("""
            from abc import ABC, abstractmethod

            class Interfaz(ABC):
                @abstractmethod
                def uno(self): ...

                @abstractmethod
                def dos(self): ...

                def helper_concreto(self):
                    return 42
        """)
        f = _py(tmp_path, "abc_mixta.py", codigo)
        resultados = _ejecutar(FatInterfaceAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_detecta_abc_via_metaclass(self, tmp_path):
        codigo = "from abc import ABCMeta, abstractmethod\n\nclass Interfaz(metaclass=ABCMeta):\n" + _metodos_abc(6)
        f = _py(tmp_path, "metaclass.py", codigo)
        resultados = _ejecutar(FatInterfaceAnalyzer(), f, DesignReviewerConfig())
        assert len(resultados) == 1

    def test_reporta_protocol_con_muchos_metodos(self, tmp_path):
        codigo = "from typing import Protocol\n\nclass Contrato(Protocol):\n" + _metodos_protocol(6)
        f = _py(tmp_path, "protocol_gordo.py", codigo)
        resultados = _ejecutar(FatInterfaceAnalyzer(), f, DesignReviewerConfig())

        assert len(resultados) == 1
        assert resultados[0].class_name == "Contrato"
        assert resultados[0].current_value == 6

    def test_no_reporta_protocol_con_pocos_metodos(self, tmp_path):
        codigo = "from typing import Protocol\n\nclass Contrato(Protocol):\n" + _metodos_protocol(3)
        f = _py(tmp_path, "protocol_chico.py", codigo)
        resultados = _ejecutar(FatInterfaceAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_no_reporta_clase_normal_sin_abc_ni_protocol(self, tmp_path):
        codigo = "class ClaseNormal:\n" + _metodos_protocol(10)
        f = _py(tmp_path, "clase_normal.py", codigo)
        resultados = _ejecutar(FatInterfaceAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_respeta_umbral_configurado(self, tmp_path):
        codigo = "from abc import ABC, abstractmethod\n\nclass Interfaz(ABC):\n" + _metodos_abc(4)
        f = _py(tmp_path, "umbral_custom.py", codigo)
        config = DesignReviewerConfig(max_abstract_methods=3)
        resultados = _ejecutar(FatInterfaceAnalyzer(), f, config)
        assert len(resultados) == 1
        assert resultados[0].threshold == 3

    def test_deshabilitado_por_config_no_ejecuta(self, tmp_path):
        codigo = "from abc import ABC, abstractmethod\n\nclass Interfaz(ABC):\n" + _metodos_abc(6)
        f = _py(tmp_path, "deshabilitado.py", codigo)
        config = DesignReviewerConfig(checks=DesignReviewerChecksConfig(fat_interface=False))
        analyzer = FatInterfaceAnalyzer()
        ctx = ExecutionContext(file_path=f, config=config)
        assert analyzer.should_run(ctx) is False

    def test_archivo_sin_clases_no_falla(self, tmp_path):
        f = _py(tmp_path, "sin_clases.py", "def funcion():\n    return 42\n")
        resultados = _ejecutar(FatInterfaceAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []
