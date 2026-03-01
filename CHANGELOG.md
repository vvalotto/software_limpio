# Changelog

Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [0.3.0] - 2026-03-01

### 🎉 ArchitectAnalyst — Análisis Arquitectónico de Fin de Sprint

Tercera release de **Software Limpio**: el agente **ArchitectAnalyst** completamente funcional. Analiza la salud arquitectónica del sistema completo al finalizar un sprint. A diferencia de los otros agentes, **nunca bloquea** — es informativo y estratégico.

### ✨ Added — Funcionalidades Nuevas

#### ArchitectAnalyst — Agente de Arquitectura (Fin de Sprint)

**Infraestructura Modular:**
- Arquitectura de métricas project-wide con auto-discovery (`MetricOrchestrator`)
- Tipos propios: `ArchitectureSeverity` (INFO/WARNING/CRITICAL), `MetricTrend` (IMPROVING/STABLE/DEGRADING), `ArchitectureResult`
- `ProjectMetric` — clase base para métricas cross-module (vs. `Verifiable` que trabaja archivo por archivo)
- `ArchitectAnalystConfig` con umbrales configurables vía `[tool.architectanalyst]`

**5 Métricas de Martin + 2 Estructurales:**

*Métricas de Robert C. Martin:*
- `CouplingAnalyzer` — Ca (Afferent Coupling) y Ce (Efferent Coupling) por módulo (INFO)
- `InstabilityAnalyzer` — I = Ce / (Ca + Ce) por módulo (WARNING si I > 0.8)
- `AbstractnessAnalyzer` — A = clases abstractas / total clases (INFO)
- `DistanceAnalyzer` — D = |A + I - 1| (WARNING si D > 0.3, CRITICAL si D > 0.5)

*Análisis Estructural:*
- `DependencyCyclesAnalyzer` — ciclos en el grafo de imports, algoritmo de Tarjan (CRITICAL)
- `LayerViolationsAnalyzer` — imports que violan la arquitectura en capas declarada en config (CRITICAL)

**Tendencias Históricas:**
- `SnapshotStore` — persiste snapshots en SQLite (`.quality_control/architecture.db`)
- `TrendCalculator` — calcula ↑↓= comparando snapshot actual vs. anterior
- Cada `ArchitectureResult` incluye `MetricTrend` con su símbolo de tendencia

**CLI Completo:**
- Comando `architectanalyst` con opciones `--format`, `--config`, `--sprint-id`
- Exit code **siempre 0** (nunca bloquea — agente informativo)
- Output Rich: tabla con métricas de Martin + columna Trend (↑↓=), sección CRÍTICAS separada
- Output JSON estructurado con `summary.should_block = false` y `trend_available`

### 🧪 Tests

- **271 tests nuevos — 788 tests totales pasando (100%)**
  - 211 tests unitarios de ArchitectAnalyst (infraestructura, métricas, tendencias, CLI)
  - 24 tests E2E con código sintético real (ciclos, capas, Martin metrics)
  - 3 tests de dogfooding sobre el propio proyecto

### 📚 Documentation

- `docs/guias/architectanalyst.md` — Guía de usuario completa (Main Sequence, tendencias, configuración de capas)
- `README.md` — Sección ArchitectAnalyst actualizada
- Diagramas del Main Sequence y tablas de métricas

### 🏗️ Infrastructure

- `pyproject.toml` actualizado a version `0.3.0`
- Entrada CLI `architectanalyst` en entry points
- `[tool.architectanalyst]` en pyproject.toml con umbrales por defecto
- Base de datos SQLite en `.quality_control/architecture.db`

---

## [0.2.0] - 2026-02-21

### 🎉 DesignReviewer — Análisis de Calidad de Diseño

Segunda release de **Software Limpio**: el agente **DesignReviewer** completamente funcional. Analiza el delta de un PR y **puede bloquear el merge** si detecta violaciones críticas de diseño.

### ✨ Added — Funcionalidades Nuevas

#### DesignReviewer — Agente de Diseño (PR Review)

**Infraestructura Modular:**
- Arquitectura de analyzers con auto-discovery (mismo patrón que CodeGuard)
- Tipos propios: `ReviewSeverity` (INFO/WARNING/CRITICAL) y `ReviewResult` con `estimated_effort`
- `AnalyzerOrchestrator` con manejo de errores por analyzer
- `DesignReviewerConfig` con umbrales configurables vía `[tool.designreviewer]`

**12 Analyzers implementados:**

*Acoplamiento:*
- `CBOAnalyzer` — Coupling Between Objects (umbral: 5, CRITICAL)
- `FanOutAnalyzer` — Fan-Out de módulos importados (umbral: 7, WARNING)
- `CircularImportsAnalyzer` — Ciclos de dependencias (CRITICAL)

*Cohesión y Herencia:*
- `LCOMAnalyzer` — Lack of Cohesion of Methods — LCOM4 via AST (umbral: 1, WARNING)
- `WMCAnalyzer` — Weighted Methods per Class via radon (umbral: 20, CRITICAL)
- `DITAnalyzer` — Depth of Inheritance Tree (umbral: 5, CRITICAL)
- `NOPAnalyzer` — Number of Parents / herencia múltiple (umbral: 1, CRITICAL)

*Code Smells + SOLID:*
- `GodObjectAnalyzer` — Clases con demasiados métodos (SRP)
- `LongMethodAnalyzer` — Métodos demasiado largos (SRP)
- `LongParameterListAnalyzer` — Listas de parámetros excesivas (ISP)
- `FeatureEnvyAnalyzer` — Envidia de funcionalidad entre clases (SRP/DIP)
- `DataClumpsAnalyzer` — Grupos de parámetros repetidos (SRP)

**CLI Completo:**
- Comando `designreviewer` con opciones `--format`, `--config`, `--no-ai`
- Exit code 1 si hay violaciones CRITICAL, 0 si no
- Output Rich: panel 🚫 BLOCKING ISSUES separado de ⚠ Advertencias
- Panel ⏱ Deuda Técnica con `estimated_effort` total del changeset
- Output JSON estructurado con `summary.should_block` para CI/CD

**`estimated_effort`:**
- Cada resultado incluye estimación de horas de refactoring
- El reporte muestra el total acumulado del changeset

### 🧪 Tests

- **517 tests pasando (100%)**
  - 20 tests E2E con código sintético real (sin mocks)
  - 18 tests de integración del CLI
  - 15 tests unitarios del formatter
  - 111 tests unitarios de los 12 analyzers
- Dogfooding: `designreviewer src/` corre sin crash sobre el propio proyecto

### 📚 Documentation

- `docs/guias/designreviewer.md` — Guía de usuario completa
- `README.md` — Sección DesignReviewer actualizada
- Tablas de métricas con umbrales y severidades

### 🏗️ Infrastructure

- `pyproject.toml` actualizado a version `0.2.0`
- Entrada CLI `designreviewer` en entry points
- `[tool.designreviewer]` en pyproject.toml con umbrales por defecto

---

## [0.1.0] - 2026-02-18

### 🎉 Primera Release - MVP CodeGuard

Esta es la primera versión pública de **Software Limpio**, incluyendo el agente **CodeGuard** completamente funcional.

### ✨ Added - Funcionalidades Nuevas

#### CodeGuard - Agente de Control de Calidad Pre-commit

**Arquitectura Modular:**
- Sistema modular de checks con auto-discovery
- Clase base `Verifiable` + `ExecutionContext`
- `CheckOrchestrator` con selección contextual inteligente
- 6 checks modulares independientes:
  - `PEP8Check` - Verificación de estilo (flake8)
  - `SecurityCheck` - Detección de vulnerabilidades (bandit)
  - `ComplexityCheck` - Análisis de complejidad ciclomática (radon)
  - `PylintCheck` - Score general de calidad (pylint)
  - `TypeCheck` - Verificación de tipos (mypy)
  - `ImportCheck` - Detección de imports sin usar (pylint)

**CLI Completo:**
- Comando `codeguard` con múltiples opciones
- `--analysis-type` (pre-commit, pr-review, full)
- `--time-budget` para límites de tiempo
- `--format` (text, json)
- `--config` para configuración personalizada

**Configuración Moderna:**
- Soporte `pyproject.toml` → `[tool.codeguard]` (PEP 518)
- Fallback a `.codeguard.yml` (YAML legacy)
- Auto-discovery de configuración
- Configuración de IA opcional (`[tool.codeguard.ai]`)

**Output Profesional:**
- Rich formatter con colores y tablas
- Output JSON estructurado con metadata completa
- Sugerencias contextuales (black, autoflake, etc.)
- Resumen ejecutivo con estadísticas

**Integración con Git:**
- Framework pre-commit con 3 hooks:
  - `codeguard` - Análisis rápido (< 5s)
  - `codeguard-pr` - Análisis PR (~10-15s)
  - `codeguard-full` - Análisis completo (~20-30s)
- Archivo `.pre-commit-hooks.yaml` incluido
- Ejemplo `.pre-commit-config.yaml.example`

**Documentación Completa:**
- Guía de usuario exhaustiva (`docs/guias/codeguard.md`)
- README técnico para contribuidores (`src/quality_agents/codeguard/README.md`)
- Documentación de mantenimiento (`docs/agentes/MANTENIMIENTO_CODEGUARD.md`)
- QUICKSTART.md - Guía de inicio rápido
- Ejemplo funcional completo (`examples/sample_project/`)

**Framework Teórico:**
- Documentación completa de 6 principios fundamentales
- Marco filosófico (4 virtudes, antifragilidad, sistemas complejos)
- Trilogía limpia (Código, Diseño, Arquitectura)
- Nuevo paradigma profesional (4 competencias)

### 🔧 Fixed - Correcciones

- **AIConfig:** Eliminado campo `model` inexistente que causaba errores de configuración

### 🧪 Tests

- **300 tests pasando (100% cobertura)**
  - 245 tests unitarios
  - 39 tests de integración
  - 16 tests end-to-end
- Tests de configuración (pyproject.toml, YAML, defaults)
- Tests de orquestación contextual
- Tests de IA (habilitada/deshabilitada, sin API key)
- Tests de pre-commit framework

### 📚 Documentation

**Documentación de Usuario:**
- `QUICKSTART.md` - Inicio en 5 minutos
- `docs/guias/codeguard.md` - Guía completa (~900 líneas)
- `README.md` - Quick start del proyecto
- `examples/sample_project/` - Proyecto de ejemplo con 23+ problemas

**Documentación Técnica:**
- `src/quality_agents/codeguard/README.md` - Arquitectura técnica (434 líneas)
- `docs/agentes/MANTENIMIENTO_CODEGUARD.md` - Guía de mantenimiento (588 líneas)
- `docs/agentes/decision_arquitectura_checks_modulares.md` - Decisión arquitectónica
- `docs/agentes/guia_implementacion_agentes.md` - Guía para implementadores

**Documentación Teórica:**
- `docs/teoria/fundamentos/` - 6 principios fundamentales
- `docs/teoria/marco_filosofico/` - Marco conceptual
- `docs/teoria/trilogia_limpia/` - Código, Diseño, Arquitectura
- `docs/teoria/nuevo_paradigma/` - Nuevo rol profesional

### 🏗️ Infrastructure

- Estructura de paquete instalable completa
- `pyproject.toml` con build-system moderno
- Entry points CLI para 3 agentes
- Configuración de herramientas (black, isort, mypy, pytest)
- `.pre-commit-hooks.yaml` para framework pre-commit
- MANIFEST.in para distribución
- LICENSE MIT

### 📦 Dependencies

**Core:**
- flake8 >= 6.0.0
- pylint >= 3.0.0
- bandit >= 1.7.5
- mypy >= 1.7.0
- radon >= 6.0.1
- anthropic >= 0.8.0 (IA opcional)
- rich >= 13.7.0 (output profesional)
- click >= 8.1.7 (CLI)
- pyyaml >= 6.0.1
- jinja2 >= 3.1.2
- plotly >= 5.17.0

**Development:**
- pytest >= 7.4.0
- pytest-cov >= 4.1.0
- black >= 23.0.0
- isort >= 5.12.0
- ruff >= 0.1.0

### 🎯 Performance

- Análisis pre-commit: **< 5 segundos** (6 archivos promedio)
- Análisis PR-review: **~10-15 segundos**
- Análisis full: **~20-30 segundos**
- Auto-discovery de checks: **< 0.1 segundos**

### 🚀 Distribution

- Paquete `quality-agents` listo para PyPI
- Versión: 0.1.0
- Python: >= 3.11
- Licencia: MIT

---

## [Unreleased]

### Próximas Funcionalidades

#### ArchitectAnalyst (v0.3.0)
- Análisis de tendencias arquitectónicas a lo largo del tiempo
- Métricas históricas en SQLite
- Dashboards interactivos con Plotly
- Detección de degradación arquitectónica

#### Mejoras Futuras
- MI (Maintainability Index) en CodeGuard via `radon mi`
- Soporte para análisis paralelo de checks
- Integración con GitHub Actions (workflows pre-configurados)
- Soporte para plugins personalizados

---

## Notas de Versión

### v0.1.0 - CodeGuard MVP

**Estado:** ✅ Completo y listo para producción

**Horas de desarrollo:** ~43 horas

**Commits:** ~50 commits en branch `fase-6-documentacion`

**Líneas de código:**
- Código fuente: ~3,500 líneas
- Tests: ~5,000 líneas
- Documentación: ~8,000 líneas

**Cobertura de tests:** 100% en módulos core

**Compatibilidad:** Python 3.11, 3.12, 3.13

**Plataformas:** macOS, Linux, Windows (experimental)

---

## Links

- [Repositorio](https://github.com/vvalotto/software_limpio)
- [Documentación](https://github.com/vvalotto/software_limpio/tree/main/docs)
- [Issues](https://github.com/vvalotto/software_limpio/issues)
- [PyPI](https://pypi.org/project/quality-agents/) (próximamente)

---

**Software Limpio** - Control de Calidad Automatizado para Python 🚀
