"""
Tests unitarios para ConcreteDependencyAnalyzer (DIP).

Ticket: Issue #74
"""

import textwrap
from pathlib import Path

from quality_agents.designreviewer.analyzers.concrete_dependency_analyzer import (
    ConcreteDependencyAnalyzer,
)
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


class TestConcreteDependencyAnalyzer:
    def test_no_reporta_con_una_o_dos_dependencias(self, tmp_path):
        f = _py(tmp_path, "pocas.py", """
            from servicios import ClienteRepo, EmailService

            class ServicioFacturacion:
                def __init__(self):
                    self.cliente = ClienteRepo()
                    self.email = EmailService()
        """)
        resultados = _ejecutar(ConcreteDependencyAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_reporta_con_tres_o_mas_dependencias(self, tmp_path):
        f = _py(tmp_path, "muchas.py", """
            from servicios import ClienteRepo, EmailService, GeneradorPDF

            class ServicioFacturacion:
                def __init__(self):
                    self.cliente = ClienteRepo()
                    self.email = EmailService()
                    self.pdf = GeneradorPDF()
        """)
        resultados = _ejecutar(ConcreteDependencyAnalyzer(), f, DesignReviewerConfig())

        assert len(resultados) == 1
        r = resultados[0]
        assert r.class_name == "ServicioFacturacion"
        assert r.severity == ReviewSeverity.WARNING
        assert r.current_value == 3
        assert r.threshold == 2
        assert r.solid_principle == SolidPrinciple.DIP
        assert r.smell_type == "ConcreteDependency"

    def test_ignora_dependencias_no_importadas_en_el_archivo(self, tmp_path):
        """Si 'ClaseLocal' se define en el mismo archivo (no importada), no cuenta."""
        f = _py(tmp_path, "clase_local.py", """
            class ClaseLocal:
                pass

            class Servicio:
                def __init__(self):
                    self.dep = ClaseLocal()
        """)
        resultados = _ejecutar(ConcreteDependencyAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_ignora_tipos_stdlib_excluidos(self, tmp_path):
        f = _py(tmp_path, "stdlib.py", """
            from pathlib import Path
            from decimal import Decimal
            from collections import defaultdict

            class Servicio:
                def __init__(self):
                    self.ruta = Path(".")
                    self.monto = Decimal("0")
                    self.cache = defaultdict(list)
        """)
        resultados = _ejecutar(ConcreteDependencyAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_ignora_instanciaciones_sin_asignar_a_self(self, tmp_path):
        f = _py(tmp_path, "sin_self.py", """
            from servicios import ClienteRepo, EmailService, GeneradorPDF

            class Servicio:
                def __init__(self):
                    self.cliente = ClienteRepo()
                    self.email = EmailService()
                    temporal = GeneradorPDF()  # variable local, no dependencia
                    temporal.generar()
        """)
        resultados = _ejecutar(ConcreteDependencyAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_ignora_instanciaciones_fuera_de_init(self, tmp_path):
        f = _py(tmp_path, "fuera_de_init.py", """
            from servicios import ClienteRepo, EmailService, GeneradorPDF

            class Servicio:
                def __init__(self):
                    self.cliente = ClienteRepo()

                def configurar(self):
                    self.email = EmailService()
                    self.pdf = GeneradorPDF()
        """)
        resultados = _ejecutar(ConcreteDependencyAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_respeta_umbral_configurado(self, tmp_path):
        f = _py(tmp_path, "umbral_custom.py", """
            from servicios import ClienteRepo, EmailService

            class Servicio:
                def __init__(self):
                    self.cliente = ClienteRepo()
                    self.email = EmailService()
        """)
        config = DesignReviewerConfig(max_concrete_dependencies=1)
        resultados = _ejecutar(ConcreteDependencyAnalyzer(), f, config)
        assert len(resultados) == 1
        assert resultados[0].threshold == 1

    def test_deshabilitado_por_config_no_ejecuta(self, tmp_path):
        f = _py(tmp_path, "deshabilitado.py", """
            from servicios import ClienteRepo, EmailService, GeneradorPDF

            class Servicio:
                def __init__(self):
                    self.cliente = ClienteRepo()
                    self.email = EmailService()
                    self.pdf = GeneradorPDF()
        """)
        config = DesignReviewerConfig(checks=DesignReviewerChecksConfig(concrete_dependency=False))
        analyzer = ConcreteDependencyAnalyzer()
        ctx = ExecutionContext(file_path=f, config=config)
        assert analyzer.should_run(ctx) is False

    def test_archivo_sin_imports_no_falla(self, tmp_path):
        f = _py(tmp_path, "sin_imports.py", """
            class Servicio:
                def __init__(self):
                    self.valor = 42
        """)
        resultados = _ejecutar(ConcreteDependencyAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []

    def test_clase_sin_init_no_falla(self, tmp_path):
        f = _py(tmp_path, "sin_init.py", """
            from servicios import ClienteRepo

            class Servicio:
                def metodo(self):
                    return ClienteRepo()
        """)
        resultados = _ejecutar(ConcreteDependencyAnalyzer(), f, DesignReviewerConfig())
        assert resultados == []
