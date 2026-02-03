"""
Checks modulares de CodeGuard.

Este paquete contiene todos los checks de calidad implementados como clases
que heredan de `Verifiable`. El orquestador (`CheckOrchestrator`) descubre
automáticamente todos los checks en este paquete y los ejecuta según el contexto.

Arquitectura Modular
====================

Cada check es una clase independiente que:
1. Hereda de `quality_agents.shared.verifiable.Verifiable`
2. Implementa las propiedades abstractas: `name`, `category`
3. Sobrescribe (opcionalmente): `estimated_duration`, `priority`, `should_run()`
4. Implementa el método abstracto: `execute(file_path)`

Auto-Discovery
==============

Los checks son descubiertos automáticamente por `CheckOrchestrator._discover_checks()`:
- El orquestador importa este módulo
- Busca todas las clases que heredan de `Verifiable`
- Las instancia y las agrega a la lista de checks disponibles

No es necesario registrar manualmente los checks, solo:
1. Crear la clase en un archivo dentro de `checks/`
2. Importarla en este `__init__.py`
3. Agregarla a `__all__`

Estructura de un Check
======================

```python
# checks/ejemplo_check.py
from pathlib import Path
from typing import List

from quality_agents.shared.verifiable import Verifiable, ExecutionContext
from quality_agents.codeguard.agent import CheckResult, Severity


class EjemploCheck(Verifiable):
    '''Descripción del check.'''

    @property
    def name(self) -> str:
        return "Ejemplo"

    @property
    def category(self) -> str:
        return "quality"  # o "style", "security", "design"

    @property
    def estimated_duration(self) -> float:
        return 1.0  # segundos

    @property
    def priority(self) -> int:
        return 3  # 1=más alta, 10=más baja

    def should_run(self, context: ExecutionContext) -> bool:
        '''Decide si debe ejecutarse en este contexto.'''
        if context.is_excluded:
            return False
        if context.file_path.suffix != ".py":
            return False
        # Verificar si está habilitado en config
        if context.config and not context.config.check_ejemplo:
            return False
        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        '''Ejecuta el check y retorna resultados.'''
        results = []
        # Implementar lógica del check aquí
        return results
```

Checks Implementados
====================

(Los checks se implementarán en la Fase 2)

Próximos checks a implementar:
- PEP8Check: Conformidad con PEP8 usando flake8
- PylintCheck: Análisis de calidad con pylint
- SecurityCheck: Vulnerabilidades con bandit
- ComplexityCheck: Complejidad ciclomática con radon
- TypeCheck: Verificación de tipos con mypy
- ImportCheck: Orden y uso de imports

Referencias
===========

- Decisión arquitectónica: docs/agentes/decision_arquitectura_checks_modulares.md
- Plan de implementación: PLAN_IMPLEMENTACION.md (Fase 2)
- Guía para contribuidores: docs/agentes/guia_implementacion_agentes.md

Fecha de creación: 2026-02-03
Ticket: 1.5.3
"""

# Cuando se implementen checks en Fase 2, importarlos aquí:
# from .pep8_check import PEP8Check
# from .pylint_check import PylintCheck
# from .security_check import SecurityCheck
# from .complexity_check import ComplexityCheck
# from .type_check import TypeCheck
# from .import_check import ImportCheck

# Lista de checks exportados (actualizar cuando se agreguen checks)
__all__ = [
    # "PEP8Check",
    # "PylintCheck",
    # "SecurityCheck",
    # "ComplexityCheck",
    # "TypeCheck",
    # "ImportCheck",
]
