# Changelog

Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [0.1.0] - 2026-02-05

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

#### Fase 7: DesignReviewer (v0.2.0)
- Análisis profundo de diseño para Pull Requests
- Detección de code smells
- Análisis de cohesión y acoplamiento
- Sugerencias de refactoring con IA

#### Fase 8: ArchitectAnalyst (v0.3.0)
- Análisis de tendencias arquitectónicas
- Métricas históricas en SQLite
- Dashboards interactivos con Plotly
- Detección de degradación arquitectónica

#### Mejoras Futuras
- Soporte para análisis paralelo de checks
- Cache de resultados para análisis incremental
- Integración con GitHub Actions (workflows pre-configurados)
- Soporte para plugins personalizados
- Dashboard web para visualización de métricas
- Análisis de dependencias y detección de ciclos

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
