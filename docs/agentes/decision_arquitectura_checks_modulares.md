# Decisión Arquitectónica: Sistema de Verificaciones/Análisis Modulares con Orquestación Contextual

**Fecha:** 2026-02-02
**Estado:** Propuesta
**Afecta a:** CodeGuard, DesignReviewer, ArchitectAnalyst
**Relacionado con:** Decisiones arquitectónicas de Enero 2026 (`ajuste_documentacion.md`)

---

## Resumen Ejecutivo

Se propone una **arquitectura modular con orquestación contextual** para las verificaciones (CodeGuard), análisis (DesignReviewer) y métricas (ArchitectAnalyst), reemplazando el diseño actual de funciones en módulos monolíticos.

**Principio rector:** Cada verificación/análisis es un componente cohesivo y autocontenido que decide cuándo debe ejecutarse según el contexto, orquestado por un componente inteligente que optimiza tiempo y relevancia.

---

## 1. Contexto

### Situación Actual

Durante la implementación de CodeGuard Fase 2 (Ticket 2.1: Check PEP8), se identificó una limitación arquitectónica en el diseño actual:

```python
# Diseño actual: src/quality_agents/codeguard/checks.py
def check_pep8(file_path: Path) -> List[CheckResult]: ...
def check_pylint_score(file_path: Path, min_score: float) -> List[CheckResult]: ...
def check_security_issues(file_path: Path) -> List[CheckResult]: ...
def check_cyclomatic_complexity(file_path: Path, max_cc: int) -> List[CheckResult]: ...
def check_type_errors(file_path: Path) -> List[CheckResult]: ...
def check_unused_imports(file_path: Path) -> List[CheckResult]: ...
```

Este patrón se replica en:
- `designreviewer/analyzers.py` (análisis de diseño)
- `architectanalyst/metrics.py` (métricas de arquitectura)

### Motivación del Cambio

**Pregunta clave planteada:** *"¿No siempre hay que medir todo, y no debería un agente determinar qué mediciones tienen sentido para un caso dado?"*

Esta pregunta revela limitaciones fundamentales del diseño actual que contradicen los principios del proyecto.

---

## 2. Problema Identificado

### 2.1 Violación de Principios Fundamentales

El diseño actual viola varios de los 6 principios fundamentales del proyecto:

| Principio | Violación | Consecuencia |
|-----------|-----------|--------------|
| **Modularidad** (Parnas 1972) | Todos los checks en un módulo monolítico | Difícil agregar/modificar checks sin afectar otros |
| **Cohesión** (Constantine 1968) | Funciones sin relación clara agrupadas | Baja cohesión funcional |
| **Acoplamiento** (Constantine 1968) | Agregar check modifica el mismo archivo | Alto acoplamiento de cambio |
| **Separación de concerns** (Dijkstra 1974) | Lógica de ejecución mezclada con lógica de decisión | No hay separación entre "qué ejecutar" y "cuándo ejecutar" |
| **Ocultamiento de información** | Detalles de implementación expuestos | No hay abstracción clara |

### 2.2 Problemas Prácticos

#### Problema 1: Falta de Contexto
No hay mecanismo para decidir **qué checks ejecutar** según:
- Tipo de análisis (pre-commit vs PR vs sprint-end)
- Archivos modificados vs nuevos
- Presupuesto de tiempo (< 5s en pre-commit)
- Relevancia (un cambio de docs no necesita análisis de complejidad)

#### Problema 2: Escalabilidad Limitada
```python
# checks.py crece linealmente con cada nuevo check
# Con 20 checks → 500+ líneas en un solo archivo
# Con 50 checks → 1250+ líneas (inmanejable)
```

#### Problema 3: Rigidez
Todos los checks se ejecutan siempre, sin considerar:
- ¿Es relevante este check para este archivo?
- ¿Tengo tiempo suficiente en el presupuesto?
- ¿Este check aporta valor en este contexto?

#### Problema 4: No Preparado para IA
El diseño actual no facilita:
- Decisión inteligente de qué medir (IA seleccionando checks)
- Adaptación según aprendizaje
- Optimización contextual

---

## 3. Solución Propuesta

### 3.1 Arquitectura Modular con Orquestación Contextual

```
Principio: "Cada verificación/análisis es un componente cohesivo que
           decide cuándo debe ejecutarse, orquestado inteligentemente"
```

### 3.2 Componentes del Diseño

#### Componente 1: Check/Analyzer/Metric Base (Abstracción)

```python
# shared/verifiable.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class ExecutionContext:
    """Contexto de ejecución para decisiones inteligentes."""

    # Información del archivo
    file_path: Path
    is_new_file: bool = False
    is_modified: bool = True

    # Contexto del análisis
    analysis_type: str = "full"  # "pre-commit", "pr-review", "full", "sprint-end"
    time_budget: Optional[float] = None  # Segundos disponibles

    # Configuración
    config: Any = None

    # Exclusiones
    is_excluded: bool = False

    # IA (opcional)
    ai_enabled: bool = False
    ai_suggestions: Optional[List[str]] = None


class Verifiable(ABC):
    """
    Clase base para todos los checks, analyzers y metrics.

    Implementa el patrón Strategy con decisión contextual.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre identificador del verificable."""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """Categoría: 'style', 'quality', 'security', 'design', 'architecture'."""
        pass

    @property
    def estimated_duration(self) -> float:
        """
        Duración estimada en segundos.

        Usado para presupuesto de tiempo en análisis rápidos.
        Default: 1.0 segundo
        """
        return 1.0

    @property
    def priority(self) -> int:
        """
        Prioridad de ejecución (1=más alta, 10=más baja).

        Usado cuando hay restricción de tiempo.
        Default: 5 (prioridad media)
        """
        return 5

    def should_run(self, context: ExecutionContext) -> bool:
        """
        Determina si este verificable debe ejecutarse en el contexto dado.

        Override en subclases para lógica específica.
        Default: siempre ejecutar si no está excluido.

        Args:
            context: Contexto de ejecución

        Returns:
            True si debe ejecutarse, False si no
        """
        return not context.is_excluded

    @abstractmethod
    def execute(self, file_path: Path) -> List[Any]:
        """
        Ejecuta la verificación/análisis.

        Args:
            file_path: Archivo a verificar/analizar

        Returns:
            Lista de resultados (CheckResult, AnalysisResult, MetricResult)
        """
        pass
```

#### Componente 2: Check Específico (Implementación)

```python
# codeguard/checks/pep8_check.py
from pathlib import Path
from typing import List
import subprocess

from quality_agents.shared.verifiable import Verifiable, ExecutionContext
from quality_agents.codeguard.agent import CheckResult, Severity


class PEP8Check(Verifiable):
    """Check de conformidad con PEP8 usando flake8."""

    @property
    def name(self) -> str:
        return "PEP8"

    @property
    def category(self) -> str:
        return "style"

    @property
    def estimated_duration(self) -> float:
        return 0.5  # Flake8 es rápido

    @property
    def priority(self) -> int:
        return 2  # Alta prioridad (estilo es importante)

    def should_run(self, context: ExecutionContext) -> bool:
        """Solo ejecutar si es archivo .py, no excluido, y check habilitado."""
        if context.is_excluded:
            return False

        if context.file_path.suffix != ".py":
            return False

        if context.config and not context.config.check_pep8:
            return False

        # En pre-commit siempre ejecutar (rápido y crítico)
        # En otros contextos, solo si hay presupuesto
        if context.analysis_type == "pre-commit":
            return True

        if context.time_budget is not None:
            return context.time_budget >= self.estimated_duration

        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        """Ejecuta flake8 y retorna resultados."""
        results: List[CheckResult] = []

        try:
            process = subprocess.run(
                ["flake8", str(file_path)],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if process.stdout:
                for line in process.stdout.strip().split("\n"):
                    if not line:
                        continue

                    parts = line.split(":", 3)
                    if len(parts) >= 4:
                        try:
                            line_number = int(parts[1])
                            message = parts[3].strip()

                            results.append(
                                CheckResult(
                                    check_name=self.name,
                                    severity=Severity.WARNING,
                                    message=f"{message}. Run 'black .' to auto-format.",
                                    file_path=str(file_path),
                                    line_number=line_number,
                                )
                            )
                        except (ValueError, IndexError):
                            continue

        except FileNotFoundError:
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="flake8 not found. Install with: pip install flake8",
                    file_path=str(file_path),
                    line_number=None,
                )
            )
        except subprocess.TimeoutExpired:
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message="flake8 check timed out",
                    file_path=str(file_path),
                    line_number=None,
                )
            )
        except Exception as e:
            results.append(
                CheckResult(
                    check_name=self.name,
                    severity=Severity.ERROR,
                    message=f"Error running flake8: {str(e)}",
                    file_path=str(file_path),
                    line_number=None,
                )
            )

        return results
```

#### Componente 3: Orquestador (Decisión Inteligente)

```python
# codeguard/orchestrator.py
from pathlib import Path
from typing import List, Type
import importlib
import inspect

from quality_agents.shared.verifiable import Verifiable, ExecutionContext
from quality_agents.codeguard.config import CodeGuardConfig


class CheckOrchestrator:
    """
    Orquesta la ejecución de checks basado en contexto.

    Responsabilidades:
    - Auto-discovery de checks
    - Selección contextual de qué ejecutar
    - Optimización de tiempo
    - Integración con IA (opcional)
    """

    def __init__(self, config: CodeGuardConfig):
        self.config = config
        self.checks = self._discover_checks()

    def _discover_checks(self) -> List[Verifiable]:
        """
        Auto-discovery de checks en codeguard/checks/.

        Busca todas las clases que hereden de Verifiable.
        """
        checks = []
        checks_module = importlib.import_module("quality_agents.codeguard.checks")

        # Iterar sobre todos los módulos en checks/
        for name in dir(checks_module):
            obj = getattr(checks_module, name)
            if (
                inspect.isclass(obj)
                and issubclass(obj, Verifiable)
                and obj is not Verifiable
            ):
                checks.append(obj())

        return checks

    def select_checks(
        self,
        context: ExecutionContext
    ) -> List[Verifiable]:
        """
        Selecciona qué checks ejecutar basado en contexto.

        Estrategias:
        1. Pre-commit: checks rápidos (<2s) y alta prioridad
        2. PR-review: todos los checks habilitados
        3. Full: todos los checks
        4. AI-guided (futuro): IA decide según diff

        Args:
            context: Contexto de ejecución

        Returns:
            Lista de checks a ejecutar, ordenados por prioridad
        """
        # Filtrar checks que deben ejecutarse
        candidates = [c for c in self.checks if c.should_run(context)]

        # Aplicar estrategia según tipo de análisis
        if context.analysis_type == "pre-commit":
            selected = self._select_for_precommit(candidates, context)
        elif context.analysis_type == "pr-review":
            selected = self._select_for_pr(candidates, context)
        elif context.ai_enabled:
            selected = self._select_with_ai(candidates, context)
        else:
            selected = candidates

        # Ordenar por prioridad (1=más alta primero)
        selected.sort(key=lambda c: c.priority)

        return selected

    def _select_for_precommit(
        self,
        candidates: List[Verifiable],
        context: ExecutionContext
    ) -> List[Verifiable]:
        """
        Pre-commit: solo checks rápidos y críticos.

        Presupuesto: 5 segundos total
        Prioridad: 1-3 (alta)
        """
        if context.time_budget is None:
            context.time_budget = 5.0

        selected = []
        time_used = 0.0

        # Ordenar por prioridad
        sorted_checks = sorted(candidates, key=lambda c: c.priority)

        for check in sorted_checks:
            # Solo alta prioridad (1-3)
            if check.priority > 3:
                continue

            # Verificar presupuesto de tiempo
            if time_used + check.estimated_duration <= context.time_budget:
                selected.append(check)
                time_used += check.estimated_duration
            else:
                break

        return selected

    def _select_for_pr(
        self,
        candidates: List[Verifiable],
        context: ExecutionContext
    ) -> List[Verifiable]:
        """PR review: todos los checks habilitados."""
        return candidates

    def _select_with_ai(
        self,
        candidates: List[Verifiable],
        context: ExecutionContext
    ) -> List[Verifiable]:
        """
        IA-guided selection (futuro).

        IA analiza el diff y sugiere qué checks son relevantes.
        Ejemplo:
        - Solo cambios de estilo → PEP8 + Imports
        - Nueva función compleja → Complejidad + Types + Security
        - Refactoring → Todos los checks
        """
        # TODO: Implementar cuando se agregue IA
        # Por ahora, fallback a selección normal
        return candidates
```

#### Componente 4: Integración en Agent

```python
# codeguard/agent.py
class CodeGuard:
    def __init__(self, config_path: Optional[Path] = None):
        self.config = load_config(config_path)
        self.orchestrator = CheckOrchestrator(self.config)
        self.results: List[CheckResult] = []

    def run(
        self,
        file_paths: List[Path],
        analysis_type: str = "full"
    ) -> List[CheckResult]:
        """
        Ejecuta checks sobre archivos.

        Args:
            file_paths: Archivos a analizar
            analysis_type: "pre-commit", "pr-review", "full"
        """
        for file_path in file_paths:
            # Crear contexto para este archivo
            context = ExecutionContext(
                file_path=file_path,
                analysis_type=analysis_type,
                config=self.config,
                is_excluded=self._is_excluded(file_path),
                ai_enabled=self.config.ai.enabled
            )

            # Seleccionar checks para este contexto
            checks = self.orchestrator.select_checks(context)

            # Ejecutar cada check
            for check in checks:
                try:
                    results = check.execute(file_path)
                    self.results.extend(results)
                except Exception as e:
                    # Log error pero continuar con otros checks
                    logger.error(f"Error in {check.name}: {e}")

        return self.results
```

---

## 4. Estructura de Directorios Propuesta

### CodeGuard

```
codeguard/
├── __init__.py
├── agent.py              # CodeGuard principal
├── config.py             # Configuración
├── orchestrator.py       # Orquestador de checks
├── checks/               # Checks modulares
│   ├── __init__.py       # Registry + exports
│   ├── pep8_check.py     # Check PEP8
│   ├── pylint_check.py   # Check Pylint
│   ├── security_check.py # Check Security (Bandit)
│   ├── complexity_check.py  # Check Complejidad (Radon)
│   ├── types_check.py    # Check Types (mypy)
│   └── imports_check.py  # Check Imports
└── PLAN_IMPLEMENTACION.md
```

### DesignReviewer

```
designreviewer/
├── __init__.py
├── agent.py              # DesignReviewer principal
├── config.py             # Configuración
├── orchestrator.py       # Orquestador de análisis
├── analyzers/            # Analizadores modulares
│   ├── __init__.py
│   ├── lcom_analyzer.py  # LCOM (cohesión)
│   ├── cbo_analyzer.py   # CBO (acoplamiento)
│   ├── mi_analyzer.py    # Maintainability Index
│   └── wmc_analyzer.py   # WMC (complejidad ponderada)
└── ai_integration.py     # Integración Claude API
```

### ArchitectAnalyst

```
architectanalyst/
├── __init__.py
├── agent.py              # ArchitectAnalyst principal
├── config.py             # Configuración
├── orchestrator.py       # Orquestador de métricas
├── metrics/              # Métricas modulares
│   ├── __init__.py
│   ├── martin_metrics.py # Métricas de Martin (I, A, D)
│   ├── stability_metrics.py  # Estabilidad (Ca, Ce)
│   └── cycles_analyzer.py    # Detección de ciclos
├── snapshots.py          # Persistencia SQLite
└── dashboard.py          # Visualización Plotly
```

### Shared (Código Común)

```
shared/
├── __init__.py
├── verifiable.py         # Clase base Verifiable + ExecutionContext
├── config.py             # QualityConfig base
└── reporting.py          # Generación de reportes
```

---

## 5. Aplicación a los Tres Agentes

### 5.1 CodeGuard

**Verificables:** Checks de calidad de código
**Contexto clave:** Presupuesto de tiempo (< 5s en pre-commit)
**Estrategias:**
- Pre-commit: solo checks rápidos y críticos
- PR-review: todos los checks
- IA: selección inteligente según diff

### 5.2 DesignReviewer

**Verificables:** Analizadores de diseño
**Contexto clave:** Tipo de cambio (refactoring vs feature nueva)
**Estrategias:**
- Refactoring: LCOM + CBO (cohesión y acoplamiento)
- Feature nueva: MI + WMC (mantenibilidad y complejidad)
- IA: sugerencias basadas en patrones detectados

### 5.3 ArchitectAnalyst

**Verificables:** Métricas de arquitectura
**Contexto clave:** Sprint (análisis de tendencias)
**Estrategias:**
- Sprint-end: todas las métricas + snapshot
- On-demand: métricas específicas según necesidad
- IA: detección de degradación arquitectónica

---

## 6. Fundamentación Teórica

### Aplicación de los 6 Principios Fundamentales

| Principio | Cómo se Aplica |
|-----------|----------------|
| **1. Modularidad** (Parnas 1972) | Cada check/analyzer/metric es un módulo independiente. Cambios en un check no afectan otros. |
| **2. Ocultamiento de información** (Parnas 1972) | Detalles de implementación de cada verificable encapsulados. Interfaz pública: `name`, `should_run()`, `execute()`. |
| **3. Cohesión** (Constantine 1968) | **Alta cohesión funcional**: cada verificable tiene una única responsabilidad claramente definida. |
| **4. Acoplamiento** (Constantine 1968) | **Bajo acoplamiento**: verificables independientes, orquestador como único punto de coordinación. |
| **5. Separación de concerns** (Dijkstra 1974) | Separación clara entre: (1) lógica de verificación, (2) decisión de cuándo ejecutar, (3) orquestación. |
| **6. Abstracción** (Liskov 1974) | Clase base `Verifiable` define contrato. Subclases implementan. Orquestador trabaja con abstracción. |

### Patrones de Diseño Aplicados

1. **Strategy Pattern**: Cada verificable es una estrategia de análisis
2. **Template Method**: `Verifiable` define template, subclases implementan pasos
3. **Registry Pattern**: Auto-discovery de verificables
4. **Chain of Responsibility**: Orquestador selecciona y ejecuta verificables en orden

---

## 7. Impacto en Documentación Existente

### Documentos a Actualizar

| Documento | Sección Afectada | Cambios Requeridos |
|-----------|------------------|-------------------|
| `especificacion_agentes_calidad.md` | Arquitectura de agentes | Agregar sección "Arquitectura Modular" |
| `guia_implementacion_agentes.md` | Patrón de implementación | Actualizar con patrón Verifiable + Orchestrator |
| `codeguard/PLAN_IMPLEMENTACION.md` | Fase 2 completa | Rediseñar tickets: crear base, migrar checks, crear orquestador |
| `CLAUDE.md` | Agent Structure | Actualizar estructura de directorios |
| `SESION.md` | Estado actual | Reflejar decisión arquitectónica |

### Nuevos Documentos Necesarios

- [ ] `docs/teoria/patrones/orquestacion_contextual.md` - Explicación del patrón
- [ ] `shared/verifiable.py` - Implementación de clase base
- [ ] Actualización de cada `PLAN_IMPLEMENTACION.md` de los 3 agentes

---

## 8. Consecuencias

### 8.1 Ventajas

| Aspecto | Beneficio |
|---------|-----------|
| **Mantenibilidad** | Agregar check nuevo = crear archivo nuevo, no modificar existente |
| **Testabilidad** | Cada verificable se prueba en aislamiento |
| **Escalabilidad** | Sistema crece sin degradar arquitectura |
| **Flexibilidad** | Decisiones contextuales (tipo análisis, tiempo, IA) |
| **Extensibilidad** | Auto-discovery permite plugins externos |
| **Consistencia** | Patrón uniforme en los 3 agentes |
| **Rendimiento** | Optimización de tiempo con presupuesto y prioridades |
| **IA-Ready** | Orquestador puede usar IA para decisiones |

### 8.2 Trade-offs

| Aspecto | Costo | Mitigación |
|---------|-------|------------|
| **Complejidad inicial** | Más archivos, más abstracciones | Documentación clara, ejemplos |
| **Overhead de discovery** | Auto-discovery toma tiempo | Lazy loading, cache de registry |
| **Curva de aprendizaje** | Desarrolladores deben entender patrón | Guía de implementación detallada |
| **Testing adicional** | Tests de orquestación + tests de checks | Fixtures compartidos, helpers |

### 8.3 Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Over-engineering inicial | Media | Bajo | Empezar simple, iterar según necesidad |
| Dificultad de debugging | Baja | Medio | Logging detallado en orquestador |
| Fragmentación excesiva | Baja | Bajo | Límite razonable de verificables (~10-15 por agente) |

---

## 9. Alternativas Consideradas

### Alternativa 1: Mantener Diseño Actual (Rechazada)

**Pros:**
- Ya implementado
- Familiar y simple

**Contras:**
- Viola principios fundamentales
- No escala
- No soporta decisiones contextuales
- No preparado para IA

**Decisión:** Rechazada. No alineada con visión del proyecto.

### Alternativa 2: Plugins Externos (Pospuesta)

**Pros:**
- Máxima extensibilidad
- Permite contribuciones de terceros

**Contras:**
- Complejidad de gestión de plugins
- Versioning y compatibilidad
- Seguridad

**Decisión:** Pospuesta para versión futura. Primero consolidar arquitectura interna.

### Alternativa 3: Configuración Declarativa (Complementaria)

**Pros:**
- Usuarios definen qué checks ejecutar en YAML/TOML
- Flexible

**Contras:**
- Requiere conocimiento previo de checks disponibles
- No aprovecha decisiones inteligentes

**Decisión:** Complementaria. Permitir configuración declarativa + orquestación automática.

---

## 10. Plan de Implementación

### Fase 0: Preparación (Antes de Código)
- [x] Crear este documento de decisión arquitectónica
- [ ] Revisar impacto en documentación existente
- [ ] Actualizar `especificacion_agentes_calidad.md`
- [ ] Actualizar `guia_implementacion_agentes.md`
- [ ] Rediseñar `PLAN_IMPLEMENTACION.md` de CodeGuard

### Fase 1: Fundamentos (Base Compartida)
- [ ] Crear `shared/verifiable.py` con clase base
- [ ] Crear `ExecutionContext` dataclass
- [ ] Tests unitarios de la clase base

### Fase 2: CodeGuard Refactorizado
- [ ] Crear `codeguard/orchestrator.py`
- [ ] Migrar `check_pep8()` a `checks/pep8_check.py`
- [ ] Implementar resto de checks como clases
- [ ] Tests de orquestación
- [ ] Integrar en `CodeGuard.run()`

### Fase 3: DesignReviewer y ArchitectAnalyst
- [ ] Aplicar patrón a DesignReviewer
- [ ] Aplicar patrón a ArchitectAnalyst
- [ ] Tests completos

### Fase 4: Optimización
- [ ] Implementar cache de registry
- [ ] Optimización de tiempo
- [ ] Integración IA en orquestador

---

## 11. Métricas de Éxito

La arquitectura será exitosa si:

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| **Cohesión** | LCOM ≤ 1 por clase | Análisis estático |
| **Acoplamiento** | CBO ≤ 3 por clase | Análisis estático |
| **Mantenibilidad** | MI > 20 | Radon |
| **Cobertura** | ≥ 80% tests | pytest --cov |
| **Rendimiento** | Pre-commit < 5s | Medición real |
| **Extensibilidad** | Agregar check en < 1h | Time-to-implement |

---

## 12. Referencias

### Principios Fundamentales
- Parnas, D.L. (1972) - "On the Criteria To Be Used in Decomposing Systems into Modules"
- Constantine, L. (1968) - "Coupling and Cohesion"
- Dijkstra, E.W. (1974) - "On the role of scientific thought"
- Liskov, B. (1974) - "Programming with Abstract Data Types"

### Documentos del Proyecto
- `docs/teoria/fundamentos/` - Los 6 principios fundamentales
- `docs/agentes/ajuste_documentacion.md` - Decisiones de Enero 2026
- `docs/agentes/especificacion_agentes_calidad.md` (v1.1)

### Patrones de Diseño
- Gamma et al. (1994) - "Design Patterns: Elements of Reusable Object-Oriented Software"
  - Strategy Pattern
  - Template Method
  - Chain of Responsibility

---

## 13. Decisión

**APROBADO PARA IMPLEMENTACIÓN** (Pendiente de revisión)

Esta arquitectura:
- ✅ Se alinea con los 6 principios fundamentales del proyecto
- ✅ Resuelve limitaciones identificadas en el diseño actual
- ✅ Es aplicable a los 3 agentes de manera consistente
- ✅ Prepara el sistema para decisiones contextuales e IA
- ✅ Escala sin degradar la arquitectura
- ✅ Mantiene el presupuesto de tiempo (< 5s en pre-commit)

**Próximos pasos:**
1. Revisar y aprobar este documento
2. Actualizar documentación existente
3. Rediseñar plan de implementación
4. Comenzar implementación incremental

---

**Fecha de creación:** 2026-02-02
**Autor:** Claude Sonnet 4.5 + Víctor Valotto
**Estado:** Propuesta (Pendiente de aprobación)
**Versión:** 1.0
