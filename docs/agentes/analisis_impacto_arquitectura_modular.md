# Análisis de Impacto: Arquitectura Modular con Orquestación Contextual

**Fecha:** 2026-02-02
**Decisión base:** `decision_arquitectura_checks_modulares.md`
**Estado:** En análisis

---

## Resumen Ejecutivo

Este documento analiza el **impacto específico** de la nueva arquitectura modular en la documentación y planes existentes del proyecto Software Limpio.

**Alcance:** Los 3 agentes (CodeGuard, DesignReviewer, ArchitectAnalyst) + documentación general

---

## 1. Documentos Afectados

### Clasificación por Nivel de Impacto

| Nivel | Documento | Líneas | Esfuerzo | Prioridad |
|-------|-----------|--------|----------|-----------|
| 🔴 **CRÍTICO** | `codeguard/PLAN_IMPLEMENTACION.md` | 500 | 4-6h | P0 |
| 🔴 **CRÍTICO** | `especificacion_agentes_calidad.md` | 1436 | 3-4h | P0 |
| 🟡 **ALTO** | `guia_implementacion_agentes.md` | 1112 | 2-3h | P1 |
| 🟡 **ALTO** | `CLAUDE.md` | - | 1-2h | P1 |
| 🟢 **MEDIO** | `SESION.md` | - | 0.5h | P2 |
| 🟢 **MEDIO** | `plan/plan_proyecto.md` | 376 | 1h | P2 |

**Total estimado:** 12-18.5 horas de trabajo de documentación

---

## 2. Análisis Detallado por Documento

### 2.1 `especificacion_agentes_calidad.md` 🔴 CRÍTICO

**Archivo:** `docs/agentes/especificacion_agentes_calidad.md`
**Tamaño:** 1436 líneas
**Impacto:** ALTO - Documento central del proyecto

#### Secciones Afectadas

##### Sección 1: Visión General (líneas 21-50)
**Cambio:** Agregar principio de "Modularidad y Cohesión"

**Contenido a agregar:**
```markdown
### Principios de Diseño (Actualizado)

1. **Separación de responsabilidades**: Cada agente opera en su contexto específico
2. **No intrusividad**: Los controles no deben paralizar el desarrollo
3. **Progresividad**: De advertencias ligeras a análisis profundos
4. **Accionabilidad**: Todo reporte debe tener sugerencias concretas
5. **Educación**: Los agentes enseñan mientras controlan
6. **Modularidad y Cohesión**: Cada verificación es un componente autocontenido (NUEVO)
```

##### Sección 2: Arquitectura del Sistema (líneas 31-41)
**Cambio:** Agregar diagrama de arquitectura interna modular

**Contenido a agregar:**
```markdown
### Arquitectura Interna (NUEVA SECCIÓN)

Cada agente implementa una **arquitectura modular con orquestación contextual**:

```
┌─────────────────────────────────────────────┐
│              AGENTE (CodeGuard)             │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────────────────────┐      │
│  │      Orchestrator                │      │
│  │  - Auto-discovery                │      │
│  │  - Selección contextual          │      │
│  │  - Presupuesto de tiempo         │      │
│  │  - Priorización                  │      │
│  └──────────┬───────────────────────┘      │
│             │                               │
│             ├─→ Check/Analyzer/Metric 1    │
│             ├─→ Check/Analyzer/Metric 2    │
│             ├─→ Check/Analyzer/Metric 3    │
│             └─→ ...                         │
│                                             │
│  Cada verificable:                         │
│  - should_run(context) → bool              │
│  - execute(file_path) → results            │
│  - estimated_duration: float               │
│  - priority: int                           │
│                                             │
└─────────────────────────────────────────────┘
```

**Características clave:**
- **Modularidad**: Cada verificación es un componente independiente
- **Orquestación**: Decisión inteligente de qué ejecutar según contexto
- **Extensibilidad**: Agregar nueva verificación = crear nuevo módulo
- **Optimización**: Presupuesto de tiempo y prioridades
```

##### Sección 3: CodeGuard - Sección completa (líneas 320-500)
**Cambio:** Agregar subsección "Arquitectura Interna"

**Contenido a agregar (después de línea 362):**

```markdown
### 1.8 Arquitectura Interna de CodeGuard

CodeGuard implementa un **sistema modular de checks** con orquestación contextual.

#### Componentes

**1. Clase Base: `Verifiable`**

Todos los checks heredan de esta clase base:

```python
class Verifiable(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del check."""
        pass

    @property
    def estimated_duration(self) -> float:
        """Duración estimada (para presupuesto)."""
        return 1.0

    @property
    def priority(self) -> int:
        """Prioridad 1=alta, 10=baja."""
        return 5

    def should_run(self, context: ExecutionContext) -> bool:
        """Decide si debe ejecutarse en este contexto."""
        return not context.is_excluded

    @abstractmethod
    def execute(self, file_path: Path) -> List[CheckResult]:
        """Ejecuta el check."""
        pass
```

**2. Checks Específicos**

Cada check es un módulo autocontenido:

- `checks/pep8_check.py` - Verificación PEP8 (flake8)
- `checks/pylint_check.py` - Análisis pylint
- `checks/security_check.py` - Seguridad (bandit)
- `checks/complexity_check.py` - Complejidad ciclomática (radon)
- `checks/types_check.py` - Type checking (mypy)
- `checks/imports_check.py` - Imports sin uso

**3. Orquestador**

El `CheckOrchestrator` decide qué checks ejecutar:

```python
class CheckOrchestrator:
    def select_checks(self, context: ExecutionContext) -> List[Verifiable]:
        """
        Selecciona checks según:
        - Tipo de análisis (pre-commit vs full)
        - Presupuesto de tiempo
        - Prioridades
        - Contexto del archivo
        - IA (opcional)
        """
```

#### Flujo de Ejecución

```
1. CodeGuard.run(files, analysis_type="pre-commit")
2. Para cada archivo:
   a. Crear ExecutionContext con info del archivo
   b. orchestrator.select_checks(context)
      - Filtrar por should_run()
      - Aplicar presupuesto de tiempo
      - Ordenar por prioridad
   c. Ejecutar cada check seleccionado
   d. Agregar resultados
3. Retornar lista de CheckResult
```

#### Ventajas de esta Arquitectura

| Aspecto | Beneficio |
|---------|-----------|
| **Mantenibilidad** | Agregar check = nuevo archivo, no modificar existente |
| **Testabilidad** | Cada check se prueba en aislamiento |
| **Flexibilidad** | Decisiones contextuales (pre-commit vs full) |
| **Rendimiento** | Solo ejecuta checks relevantes y dentro de presupuesto |
| **Extensibilidad** | Auto-discovery permite plugins futuros |

#### Decisión Contextual

Ejemplo de decisión en pre-commit:

```python
context = ExecutionContext(
    file_path=Path("src/utils.py"),
    analysis_type="pre-commit",
    time_budget=5.0,  # 5 segundos máximo
    config=config
)

# Orquestador selecciona solo checks:
# - Rápidos (< 2s cada uno)
# - Alta prioridad (1-3)
# - Que should_run() retorne True

# Resultado: PEP8 (0.5s, p=2) + Security (1.5s, p=1)
# Total: 2s de 5s disponibles
# Checks omitidos: Pylint (lento), Types (baja prioridad)
```
```

##### Sección 4: DesignReviewer (actualizar similar a CodeGuard)
**Cambio:** Agregar subsección "Arquitectura Interna"

**Contenido a agregar:**
```markdown
### 2.X Arquitectura Interna de DesignReviewer

DesignReviewer implementa un **sistema modular de analyzers** con orquestación contextual.

#### Analizadores Modulares

- `analyzers/lcom_analyzer.py` - Cohesión (LCOM)
- `analyzers/cbo_analyzer.py` - Acoplamiento (CBO)
- `analyzers/mi_analyzer.py` - Índice de Mantenibilidad
- `analyzers/wmc_analyzer.py` - Complejidad Ponderada

Cada analizador hereda de `Verifiable` y puede decidir cuándo debe ejecutarse según el contexto del análisis.
```

##### Sección 5: ArchitectAnalyst (actualizar similar)
**Cambio:** Agregar subsección "Arquitectura Interna"

**Contenido a agregar:**
```markdown
### 3.X Arquitectura Interna de ArchitectAnalyst

ArchitectAnalyst implementa un **sistema modular de metrics** con orquestación contextual.

#### Métricas Modulares

- `metrics/martin_metrics.py` - Métricas de Martin (I, A, D)
- `metrics/stability_metrics.py` - Estabilidad (Ca, Ce)
- `metrics/cycles_analyzer.py` - Detección de ciclos de dependencias

Cada métrica hereda de `Verifiable` y se ejecuta según el tipo de análisis (sprint-end, on-demand).
```

**Esfuerzo estimado:** 3-4 horas

---

### 2.2 `guia_implementacion_agentes.md` 🟡 ALTO

**Archivo:** `docs/agentes/guia_implementacion_agentes.md`
**Tamaño:** 1112 líneas
**Impacto:** ALTO - Guía de uso para desarrolladores

#### Secciones Afectadas

##### Sección Nueva: Arquitectura Interna
**Ubicación:** Después de "INSTALACIÓN RÁPIDA" (línea ~50)

**Contenido a agregar:**
```markdown
---

## ARQUITECTURA INTERNA (PARA CONTRIBUIDORES)

Esta sección es relevante si estás **contribuyendo al framework** o extendiendo funcionalidad.

### Sistema Modular de Verificaciones

Cada agente usa una arquitectura modular:

```
agente/
├── orchestrator.py       # Orquestador de verificaciones
├── checks/               # O analyzers/ o metrics/
│   ├── __init__.py
│   ├── verificable_1.py
│   ├── verificable_2.py
│   └── ...
```

### Crear un Nuevo Check/Analyzer/Metric

**Paso 1:** Crear módulo en directorio correspondiente

```python
# Ejemplo: codeguard/checks/mi_nuevo_check.py

from pathlib import Path
from typing import List

from quality_agents.shared.verifiable import Verifiable, ExecutionContext
from quality_agents.codeguard.agent import CheckResult, Severity


class MiNuevoCheck(Verifiable):
    """Descripción del check."""

    @property
    def name(self) -> str:
        return "MiNuevoCheck"

    @property
    def category(self) -> str:
        return "quality"  # o "style", "security", etc.

    @property
    def estimated_duration(self) -> float:
        return 1.5  # segundos estimados

    @property
    def priority(self) -> int:
        return 3  # 1=alta, 10=baja

    def should_run(self, context: ExecutionContext) -> bool:
        """Decide si debe ejecutarse."""
        # Ejemplo: solo archivos .py no excluidos
        if context.is_excluded:
            return False
        if context.file_path.suffix != ".py":
            return False
        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        """Ejecuta la verificación."""
        results = []

        # Tu lógica aquí
        # ...

        return results
```

**Paso 2:** Exportar en `__init__.py`

```python
# codeguard/checks/__init__.py

from .pep8_check import PEP8Check
from .pylint_check import PylintCheck
from .mi_nuevo_check import MiNuevoCheck  # AGREGAR

__all__ = [
    "PEP8Check",
    "PylintCheck",
    "MiNuevoCheck",  # AGREGAR
]
```

**Paso 3:** ¡Listo! El orquestador lo descubre automáticamente

No necesitas modificar ningún otro archivo. El sistema de auto-discovery incluirá tu check automáticamente.

### Crear Tests para tu Check

```python
# tests/unit/test_codeguard_checks.py

class TestMiNuevoCheck:
    """Tests para MiNuevoCheck."""

    def test_should_run_on_py_files(self, tmp_path):
        """Debe ejecutarse en archivos .py."""
        check = MiNuevoCheck()
        context = ExecutionContext(
            file_path=tmp_path / "test.py",
            is_excluded=False
        )
        assert check.should_run(context) is True

    def test_execute_returns_results(self, tmp_path):
        """Debe retornar lista de resultados."""
        check = MiNuevoCheck()
        file_path = tmp_path / "test.py"
        file_path.write_text("# codigo")

        results = check.execute(file_path)

        assert isinstance(results, list)
```

---
```

**Esfuerzo estimado:** 2-3 horas

---

### 2.3 `codeguard/PLAN_IMPLEMENTACION.md` 🔴 CRÍTICO

**Archivo:** `src/quality_agents/codeguard/PLAN_IMPLEMENTACION.md`
**Tamaño:** 500 líneas
**Impacto:** CRÍTICO - Rediseño completo de Fase 2

#### Cambios Requeridos

**REDISEÑO COMPLETO DE FASE 2**

La Fase 2 actual (tickets 2.1-2.6) asume funciones en `checks.py`. Con la nueva arquitectura, necesitamos:

##### Nueva Fase 1.5: Fundamentos de Arquitectura Modular (NUEVA)

```markdown
### Fase 1.5: Fundamentos de Arquitectura Modular 🎯 PRIORIDAD CRÍTICA

**Objetivo:** Crear infraestructura base para sistema modular

#### Ticket 1.5.1: Crear clase base Verifiable
- **Archivo:** `src/quality_agents/shared/verifiable.py` (nuevo)
- **Descripción:** Implementar clase base abstracta `Verifiable` y `ExecutionContext`
- **Criterios de aceptación:**
  - [ ] Crear dataclass `ExecutionContext` con campos documentados
  - [ ] Crear clase abstracta `Verifiable` con métodos requeridos
  - [ ] Properties: `name`, `category`, `estimated_duration`, `priority`
  - [ ] Métodos: `should_run()`, `execute()`
  - [ ] Documentación completa con docstrings
  - [ ] Tests unitarios de la clase base
- **Estimación:** 2-3 horas

#### Ticket 1.5.2: Crear CheckOrchestrator
- **Archivo:** `src/quality_agents/codeguard/orchestrator.py` (nuevo)
- **Descripción:** Implementar orquestador de checks
- **Criterios de aceptación:**
  - [ ] Método `_discover_checks()` con auto-discovery
  - [ ] Método `select_checks(context)` con lógica de selección
  - [ ] Estrategias: `_select_for_precommit()`, `_select_for_pr()`
  - [ ] Manejo de presupuesto de tiempo
  - [ ] Ordenamiento por prioridad
  - [ ] Tests con mocks de checks
- **Estimación:** 3-4 horas

#### Ticket 1.5.3: Crear estructura de directorios
- **Archivo:** `src/quality_agents/codeguard/checks/` (nuevo directorio)
- **Descripción:** Crear estructura modular de checks
- **Criterios de aceptación:**
  - [ ] Crear directorio `codeguard/checks/`
  - [ ] Crear `checks/__init__.py` con exports
  - [ ] Crear archivo base para futuras migraciones
- **Estimación:** 0.5 horas

**Total Fase 1.5:** 5.5-7.5 horas
```

##### Fase 2 Rediseñada: Migración de Checks a Arquitectura Modular

```markdown
### Fase 2: Migración a Arquitectura Modular 🎯 PRIORIDAD ALTA

**Objetivo:** Migrar checks existentes a clases modulares

#### Ticket 2.1: Migrar check_pep8 a PEP8Check ✅ PARCIALMENTE COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/checks/pep8_check.py` (nuevo)
- **Descripción:** Convertir función `check_pep8()` en clase `PEP8Check`
- **Criterios de aceptación:**
  - [x] Implementación funcional de check_pep8 existe
  - [ ] Crear clase `PEP8Check(Verifiable)`
  - [ ] Migrar lógica de función a método `execute()`
  - [ ] Implementar `should_run()` con lógica contextual
  - [ ] Definir `estimated_duration = 0.5` y `priority = 2`
  - [ ] Actualizar tests para usar clase
  - [ ] Deprecar función antigua
- **Estimación:** 2 horas (reducido porque ya existe implementación)

#### Ticket 2.2: Implementar PylintCheck como clase
- **Archivo:** `src/quality_agents/codeguard/checks/pylint_check.py` (nuevo)
- **Descripción:** Implementar check de pylint como clase modular
- **Criterios de aceptación:**
  - [ ] Crear clase `PylintCheck(Verifiable)`
  - [ ] Ejecutar pylint via subprocess
  - [ ] Parsear score del output
  - [ ] Comparar con `min_score` del config
  - [ ] `estimated_duration = 2.0`, `priority = 4`
  - [ ] Tests completos
- **Estimación:** 2-3 horas

#### Ticket 2.3: Implementar SecurityCheck como clase
- **Archivo:** `src/quality_agents/codeguard/checks/security_check.py` (nuevo)
- **Criterios de aceptación:**
  - [ ] Crear clase `SecurityCheck(Verifiable)`
  - [ ] Ejecutar bandit con formato JSON
  - [ ] Parsear issues HIGH → ERROR, MEDIUM → WARNING
  - [ ] `estimated_duration = 1.5`, `priority = 1` (máxima prioridad)
  - [ ] Tests con código inseguro
- **Estimación:** 3 horas

#### Ticket 2.4: Implementar ComplexityCheck como clase
- **Archivo:** `src/quality_agents/codeguard/checks/complexity_check.py` (nuevo)
- **Criterios de aceptación:**
  - [ ] Crear clase `ComplexityCheck(Verifiable)`
  - [ ] Ejecutar radon cc
  - [ ] Parsear funciones con CC > max_cc
  - [ ] `estimated_duration = 1.0`, `priority = 5`
  - [ ] Tests con función compleja
- **Estimación:** 2 horas

#### Ticket 2.5: Implementar TypesCheck como clase
- **Archivo:** `src/quality_agents/codeguard/checks/types_check.py` (nuevo)
- **Criterios de aceptación:**
  - [ ] Crear clase `TypesCheck(Verifiable)`
  - [ ] Detectar si archivo tiene type hints primero
  - [ ] Ejecutar mypy si tiene hints
  - [ ] `should_run()` retorna False si no hay hints
  - [ ] `estimated_duration = 2.0`, `priority = 6`
  - [ ] Tests con/sin hints
- **Estimación:** 2-3 horas

#### Ticket 2.6: Implementar ImportsCheck como clase
- **Archivo:** `src/quality_agents/codeguard/checks/imports_check.py` (nuevo)
- **Criterios de aceptación:**
  - [ ] Crear clase `ImportsCheck(Verifiable)`
  - [ ] Usar pylint o autoflake para detectar
  - [ ] `estimated_duration = 1.0`, `priority = 3`
  - [ ] Tests con imports sin uso
- **Estimación:** 2 horas

**Total Fase 2:** 13-16 horas (sin cambios en estimación total)
```

##### Nueva Fase 2.5: Integración con Orquestador

```markdown
### Fase 2.5: Integración con Orquestador 🎯 PRIORIDAD ALTA

**Objetivo:** Conectar checks modulares con el agente principal

#### Ticket 2.5.1: Integrar orquestador en CodeGuard.run()
- **Archivo:** `src/quality_agents/codeguard/agent.py`
- **Descripción:** Usar orquestador para seleccionar y ejecutar checks
- **Criterios de aceptación:**
  - [ ] Instanciar `CheckOrchestrator` en `__init__()`
  - [ ] En `run()`, crear `ExecutionContext` para cada archivo
  - [ ] Llamar `orchestrator.select_checks(context)`
  - [ ] Ejecutar checks seleccionados
  - [ ] Agregar manejo de errores
  - [ ] Tests de integración
- **Estimación:** 2-3 horas

#### Ticket 2.5.2: Tests de orquestación end-to-end
- **Archivo:** `tests/integration/test_codeguard_orchestration.py` (nuevo)
- **Descripción:** Probar flujo completo con múltiples checks
- **Criterios de aceptación:**
  - [ ] Test pre-commit: solo checks rápidos y prioritarios
  - [ ] Test full: todos los checks
  - [ ] Test con presupuesto de tiempo limitado
  - [ ] Test con diferentes contextos (archivo .py, .txt, excluido)
  - [ ] Verificar orden de ejecución por prioridad
- **Estimación:** 2-3 horas

**Total Fase 2.5:** 4-6 horas
```

**Impacto en estimaciones totales:**
- Fase 1.5 (nueva): +5.5-7.5h
- Fase 2 (sin cambio): 13-16h
- Fase 2.5 (nueva): +4-6h
- **Total agregado:** +23-29.5h vs 13-16h original
- **Incremento:** ~10-13.5h adicionales por arquitectura modular

**Esfuerzo estimado:** 4-6 horas de rediseño del plan

---

### 2.4 `CLAUDE.md` 🟡 ALTO

**Archivo:** `CLAUDE.md`
**Impacto:** ALTO - Guía principal para Claude Code

#### Secciones a Actualizar

##### Sección: Agent Structure
**Cambio:** Actualizar estructura de directorios

**Antes:**
```markdown
Each agent follows the same pattern in `src/quality_agents/<agent>/`:
- `agent.py` - Main class with `run()` method
- `checks.py` or `analyzers.py` - Individual verification functions
- `config.py` - Agent-specific configuration
```

**Después:**
```markdown
Each agent follows the same pattern in `src/quality_agents/<agent>/`:
- `agent.py` - Main class with `run()` method
- `orchestrator.py` - Orchestrates execution of verifiables
- `checks/` or `analyzers/` or `metrics/` - Individual verifiable components (modular)
  - Each verifiable inherits from `shared.verifiable.Verifiable`
  - Auto-discovered by orchestrator
- `config.py` - Agent-specific configuration

Shared utilities in `src/quality_agents/shared/`:
- `verifiable.py` - Base class `Verifiable` + `ExecutionContext`
- `config.py` - `QualityConfig` dataclass
- `reporting.py` - Report generation utilities
```

##### Nueva Sección: Modular Architecture
**Ubicación:** Después de "Agent Structure"

**Contenido a agregar:**
```markdown
### Modular Architecture

All agents implement a **modular verification system** with contextual orchestration:

**Base Class:**
All verifiables (checks/analyzers/metrics) inherit from `Verifiable`:
- `name` - Identifier
- `category` - Type of verification
- `estimated_duration` - Time budget
- `priority` - Execution priority (1=highest)
- `should_run(context)` - Decides if should execute
- `execute(file_path)` - Performs verification

**Orchestrator:**
Intelligently selects which verifiables to run based on:
- Analysis type (pre-commit, PR-review, full, sprint-end)
- Time budget (< 5s for pre-commit)
- File context (new, modified, excluded)
- Priorities and estimated durations
- AI suggestions (optional)

**Adding a New Check:**
1. Create new file in `checks/` directory
2. Inherit from `Verifiable`
3. Implement required methods
4. Export in `__init__.py`
5. Auto-discovery handles the rest
```

**Esfuerzo estimado:** 1-2 horas

---

### 2.5 `SESION.md` 🟢 MEDIO

**Archivo:** `SESION.md`
**Impacto:** MEDIO - Actualizar estado actual

#### Cambios Requeridos

##### Sección: Estado Actual
**Agregar entrada:**

```markdown
- [x] **Decisión arquitectónica**: Arquitectura modular con orquestación contextual
  - [x] Documento `decision_arquitectura_checks_modulares.md` creado
  - [x] Análisis de impacto completado
  - [ ] Documentación actualizada
  - [ ] Plan de implementación rediseñado
```

##### Sección: Completado
**Agregar:**

```markdown
- [x] **Decisiones arquitectónicas** (Febrero 2026)
  - [x] Sistema modular de verificaciones (checks/analyzers/metrics)
  - [x] Orquestación contextual con presupuesto de tiempo
  - [x] Clase base `Verifiable` para todos los componentes
  - [x] Auto-discovery de verificables
```

##### Sección: En Progreso
**Actualizar:**

```markdown
- [ ] **Fase 1.5: Fundamentos de Arquitectura Modular** (Nueva)
  - [ ] Crear clase base `Verifiable`
  - [ ] Implementar `CheckOrchestrator`
  - [ ] Estructura de directorios modular
- [ ] **Fase 2: Migración a Arquitectura Modular** (Rediseñada)
  - [ ] Migrar check_pep8 a clase PEP8Check
  - [ ] Implementar resto de checks como clases
```

**Esfuerzo estimado:** 0.5 horas

---

### 2.6 `plan/plan_proyecto.md` 🟢 MEDIO

**Archivo:** `plan/plan_proyecto.md`
**Impacto:** MEDIO - Ajustar estimaciones de Fase 1

#### Cambios Requeridos

##### Tabla de Fase 1
**Actualizar estimaciones:**

```markdown
| Tarea | Prioridad | Estado | Descripción |
|-------|-----------|--------|-------------|
| CLI con click | P1 | ✅ | Función `main()` |
| **Arquitectura modular base** | **P0** | **⏳** | **Clase Verifiable + Orchestrator** |
| Carga de config desde pyproject.toml | P1 | ✅ | Leer `[tool.codeguard]` |
| Check: PEP8/flake8 | P1 | ⏳ | Migrar a clase PEP8Check |
| Check: Pylint score | P1 | ⏳ | Clase PylintCheck |
| Check: Seguridad/bandit | P1 | ⏳ | Clase SecurityCheck |
| Check: Complejidad/radon | P1 | ⏳ | Clase ComplexityCheck |
| IA opcional para explicaciones | P1 | ⏳ | Claude API (opt-in) |
| Salida formateada con Rich | P1 | ⏳ | Output colorido |
| Crear `.pre-commit-hooks.yaml` | P1 | ⏳ | Soporte pre-commit |
| Documentación README | P1 | ⏳ | Instalación y uso |
| Tests de integración | P2 | ⏳ | Con orquestación |
```

**Esfuerzo estimado:** 1 hora

---

## 3. Nuevos Documentos Necesarios

### 3.1 Documentación Teórica

#### `docs/teoria/patrones/orquestacion_contextual.md` (NUEVO)

**Propósito:** Explicar el patrón de orquestación contextual

**Contenido:**
- Definición del patrón
- Por qué importa
- Cómo se aplica en Software Limpio
- Ejemplos prácticos
- Relación con principios fundamentales

**Esfuerzo:** 2-3 horas

---

## 4. Plan de Actualización de Documentación

### Orden Recomendado

| Prioridad | Documento | Esfuerzo | Dependencias |
|-----------|-----------|----------|--------------|
| **P0** | `decision_arquitectura_checks_modulares.md` | ✅ | - |
| **P0** | `analisis_impacto_arquitectura_modular.md` | ✅ | - |
| **P1** | `codeguard/PLAN_IMPLEMENTACION.md` | 4-6h | Decisión aprobada |
| **P1** | `especificacion_agentes_calidad.md` | 3-4h | Plan rediseñado |
| **P2** | `guia_implementacion_agentes.md` | 2-3h | Especificación actualizada |
| **P2** | `CLAUDE.md` | 1-2h | Especificación actualizada |
| **P3** | `SESION.md` | 0.5h | Todos los anteriores |
| **P3** | `plan/plan_proyecto.md` | 1h | Plan de CodeGuard |
| **P3** | `docs/teoria/patrones/orquestacion_contextual.md` | 2-3h | Opcional |

**Total:** 14-22.5 horas de documentación

---

## 5. Checklist de Actualización

### Fase 0: Preparación ✅
- [x] Crear documento de decisión arquitectónica
- [x] Crear análisis de impacto
- [ ] Revisar y aprobar decisión con equipo

### Fase 1: Planes de Implementación
- [ ] Rediseñar `codeguard/PLAN_IMPLEMENTACION.md`
- [ ] Crear plan para DesignReviewer (aplicar mismo patrón)
- [ ] Crear plan para ArchitectAnalyst (aplicar mismo patrón)

### Fase 2: Especificación Técnica
- [ ] Actualizar `especificacion_agentes_calidad.md`
  - [ ] Agregar principio de modularidad
  - [ ] Agregar arquitectura interna
  - [ ] Actualizar secciones de cada agente

### Fase 3: Guías de Uso
- [ ] Actualizar `guia_implementacion_agentes.md`
  - [ ] Agregar sección de arquitectura interna
  - [ ] Guía de creación de verificables

### Fase 4: Documentación Auxiliar
- [ ] Actualizar `CLAUDE.md`
- [ ] Actualizar `SESION.md`
- [ ] Actualizar `plan/plan_proyecto.md`

### Fase 5: Documentación Teórica (Opcional)
- [ ] Crear `docs/teoria/patrones/orquestacion_contextual.md`

---

## 6. Riesgos Identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Documentación desincronizada con código | Alta | Alto | Actualizar docs ANTES de implementar |
| Esfuerzo subestimado | Media | Medio | Buffer de 20% en estimaciones |
| Cambios durante implementación | Media | Medio | Documentar cambios incrementales |
| Inconsistencia entre agentes | Baja | Alto | Revisar patrón aplicado a los 3 agentes |

---

## 7. Métricas de Éxito

La actualización de documentación será exitosa si:

- [ ] Todos los documentos P0-P2 actualizados
- [ ] Arquitectura explicada consistentemente en todos los docs
- [ ] Ejemplos de código actualizados
- [ ] Guías claras para contribuidores
- [ ] Planes de implementación coherentes
- [ ] Sin referencias a diseño antiguo (funciones en `checks.py`)

---

## 8. Aprobaciones Necesarias

Antes de proceder con actualizaciones:

- [ ] Aprobación de decisión arquitectónica
- [ ] Revisión de análisis de impacto
- [ ] Acuerdo en orden de actualización
- [ ] Asignación de responsables (si aplica)

---

**Fecha de creación:** 2026-02-02
**Autor:** Claude Sonnet 4.5 + Víctor Valotto
**Estado:** Completado
**Versión:** 1.0
