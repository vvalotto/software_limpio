"""
Analyzers modulares de DesignReviewer.

Este paquete contiene todos los analyzers de calidad de diseño implementados como clases
que heredan de `Verifiable`. El orquestador (`AnalyzerOrchestrator`) descubre
automáticamente todos los analyzers en este paquete y los ejecuta sobre el changeset.

Arquitectura Modular
====================

Cada analyzer es una clase independiente que:
1. Hereda de `quality_agents.shared.verifiable.Verifiable`
2. Implementa las propiedades abstractas: `name`, `category`
3. Sobrescribe (opcionalmente): `estimated_duration`, `priority`, `should_run()`
4. Implementa el método abstracto: `execute(file_path)`

Auto-Discovery
==============

Los analyzers son descubiertos automáticamente por `AnalyzerOrchestrator._discover_analyzers()`:
- El orquestador importa este módulo
- Busca todas las clases que heredan de `Verifiable`
- Las instancia y las agrega a la lista de analyzers disponibles

No es necesario registrar manualmente los analyzers, solo:
1. Crear la clase en un archivo dentro de `analyzers/`
2. Importarla en este `__init__.py`
3. Agregarla a `__all__`

Estructura de un Analyzer
==========================

```python
# analyzers/ejemplo_analyzer.py
from pathlib import Path

from quality_agents.shared.verifiable import ExecutionContext, Verifiable
from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity


class EjemploAnalyzer(Verifiable):
    '''Descripción del analyzer.'''

    @property
    def name(self) -> str:
        return "EjemploAnalyzer"

    @property
    def category(self) -> str:
        return "coupling"  # o "cohesion", "inheritance", "smells"

    @property
    def estimated_duration(self) -> float:
        return 1.0  # segundos

    @property
    def priority(self) -> int:
        return 3  # 1=más alta, 10=más baja

    def should_run(self, context: ExecutionContext) -> bool:
        '''Decide si debe ejecutarse en este contexto.'''
        return context.file_path.suffix == ".py"

    def execute(self, file_path: Path) -> list[ReviewResult]:
        '''Ejecuta el analyzer y retorna resultados.'''
        results = []
        # Implementar lógica del analyzer aquí
        return results
```

Analyzers Implementados
========================

(Los analyzers se implementarán en las Fases 2, 3 y 4)

Fase 2 — Acoplamiento:
- CBOAnalyzer: Coupling Between Objects
- FanOutAnalyzer: Fan-Out de módulos importados
- CircularImportsAnalyzer: Ciclos de importación

Fase 3 — Cohesión y Herencia:
- LCOMAnalyzer: Lack of Cohesion of Methods
- WMCAnalyzer: Weighted Methods per Class
- DITAnalyzer: Depth of Inheritance Tree
- NOPAnalyzer: Number of Parents

Fase 4 — Code Smells y SOLID:
- GodObjectAnalyzer: clase con demasiadas responsabilidades (SRP)
- LongMethodAnalyzer: métodos con demasiadas líneas (SRP)
- LongParameterListAnalyzer: métodos con demasiados parámetros (ISP)
- FeatureEnvyAnalyzer: método que usa más datos de otra clase que los propios (SRP)
- DataClumpsAnalyzer: grupos de parámetros que siempre aparecen juntos (SRP)

Referencias
===========

- Plan de release: gestion/releases/v0.2.0-plan.md
- Especificación: docs/agentes/especificacion_agentes_calidad.md

Fecha de creación: 2026-02-19
Ticket: 1.1
"""

# Imports de analyzers implementados
from .cbo_analyzer import CBOAnalyzer
from .circular_imports_analyzer import CircularImportsAnalyzer
from .fan_out_analyzer import FanOutAnalyzer
from .dit_analyzer import DITAnalyzer
from .lcom_analyzer import LCOMAnalyzer
from .nop_analyzer import NOPAnalyzer
from .wmc_analyzer import WMCAnalyzer
from .god_object_analyzer import GodObjectAnalyzer
from .long_method_analyzer import LongMethodAnalyzer

__all__ = [
    "CBOAnalyzer",
    "CircularImportsAnalyzer",
    "DITAnalyzer",
    "FanOutAnalyzer",
    "GodObjectAnalyzer",
    "LCOMAnalyzer",
    "LongMethodAnalyzer",
    "NOPAnalyzer",
    "WMCAnalyzer",
]
