# Plan de Implementación - CodeGuard

**Fecha de creación:** 2026-01-20
**Última actualización:** 2026-02-04 (Fases 1.5, 2, 2.5 y 4 Completadas)
**Estado:** En Progreso (85% completo)
**Versión objetivo:** 0.1.0 (MVP Funcional con Arquitectura Modular)

---

## Contexto

Este documento define el plan de implementación/refactorización de CodeGuard alineado con:
- **Decisiones arquitectónicas (Enero 2026)** en `docs/agentes/ajuste_documentacion.md`
- **Decisión arquitectónica (Febrero 2026)** en `docs/agentes/decision_arquitectura_checks_modulares.md`
- **Especificación v1.1** en `docs/agentes/especificacion_agentes_calidad.md`
- **Plan general** en `plan/plan_proyecto.md`

### Cambio Arquitectónico (2026-02-02)

El plan fue **rediseñado** para implementar una **arquitectura modular con orquestación contextual**:

**Antes:** Funciones en `checks.py` monolítico
```python
def check_pep8(file_path) -> List[CheckResult]: ...
def check_pylint_score(file_path) -> List[CheckResult]: ...
# ... más funciones
```

**Después:** Clases modulares con orquestación inteligente
```python
class PEP8Check(Verifiable):
    def should_run(context) -> bool: ...
    def execute(file_path) -> List[CheckResult]: ...

# Orquestador decide qué checks ejecutar según contexto
orchestrator.select_checks(context)
```

**Beneficios:** Modularidad, cohesión, extensibilidad, decisiones contextuales, preparado para IA.

Ver detalles completos en: `docs/agentes/decision_arquitectura_checks_modulares.md`

---

## Objetivos del MVP

CodeGuard debe ser un agente funcional que:
1. ✅ Se ejecuta en < 5 segundos (< 2s sin errores)
2. ✅ Lee configuración desde `pyproject.toml` (con fallback a `.yml`)
3. ✅ Ejecuta 6 checks de calidad (flake8, pylint, bandit, radon, mypy, imports) **de forma modular**
4. ✅ **Decide contextualmente** qué checks ejecutar (nuevo objetivo)
5. ✅ Usa IA opcional para explicar errores (opt-in)
6. ✅ Genera output formateado con Rich
7. ✅ Es instalable como paquete y usable desde CLI
8. ✅ Soporta pre-commit framework

---

## Estado Actual

### ✅ Implementado (65%)

**Fase 1: Configuración Moderna** ✅ COMPLETADA
- [x] Estructura básica de clases (`CodeGuard`, `CheckResult`, `Severity`)
- [x] CLI con click (`agent.py:main()`)
- [x] Método `collect_files()` funcional
- [x] Dataclass `CodeGuardConfig` para configuración
- [x] Carga desde YAML (método `from_yaml()`)
- [x] Carga desde `pyproject.toml` (método `from_pyproject_toml()`)
- [x] Función `load_config()` con búsqueda automática
- [x] Configuración de IA en `AIConfig`
- [x] Entry point en `pyproject.toml` (`codeguard` command)
- [x] 19 tests unitarios de configuración pasando

**Fase 1.5: Fundamentos de Arquitectura Modular** ✅ COMPLETADA
- [x] Clase base `Verifiable` + `ExecutionContext` (shared/verifiable.py - 236 líneas)
- [x] `CheckOrchestrator` con auto-discovery (orchestrator.py - 285 líneas)
- [x] Estructura de directorios modular (checks/)
- [x] 71 tests pasando (14 + 13 tests)

**Fase 2: Migración a Arquitectura Modular** ✅ COMPLETADA
- [x] PEP8Check (priority=2, 0.5s) - 15 tests
- [x] PylintCheck (priority=4, 2.0s) - 23 tests
- [x] SecurityCheck (priority=1, 1.5s) - 24 tests
- [x] ComplexityCheck (priority=3, 1.0s) - 27 tests
- [x] TypeCheck (priority=5, 3.0s) - 35 tests
- [x] ImportCheck (priority=6, 0.5s) - 25 tests
- [x] 6/6 checks implementados como clases modulares
- [x] 149 tests nuevos (220 tests totales)

**Fase 2.5: Integración con Orquestador** ✅ COMPLETADA
- [x] Orquestador integrado en `CodeGuard.run()`
- [x] CLI con `--analysis-type` (pre-commit/pr-review/full)
- [x] CLI con `--time-budget`
- [x] Creación de `ExecutionContext` por archivo
- [x] Selección contextual de checks
- [x] Manejo robusto de errores
- [x] 15 tests de integración
- [x] 16 tests end-to-end
- [x] 251 tests totales pasando (100%)

**Fase 4: Output Formateado con Rich** ✅ COMPLETADA (2026-02-04)
- [x] **Ticket 4.1**: Implementar formatter con Rich (~3-4h)
  - [x] Creado `formatter.py` (325 líneas)
  - [x] Función `format_results()` con Rich Console, Panel, Table
  - [x] Header, estadísticas, tablas por severidad, sugerencias
  - [x] 18 tests unitarios
  - [x] **Commit 1aed60c** en branch `fase-4-output-rich`
- [x] **Ticket 4.2**: Agregar modo JSON (~1-2h)
  - [x] Función `format_json()` con estructura completa
  - [x] Summary, results, by_severity, timestamp
  - [x] 7 tests unitarios
  - [x] **Commit d5b1c44** en branch `fase-4-output-rich`
- [x] **Ticket 4.3**: Integrar formatter en agent.py (~1h)
  - [x] Modificado `main()` para usar formatters
  - [x] Medición de tiempo de ejecución
  - [x] Output limpio según formato (text/json)
  - [x] Tests e2e actualizados (16 tests)
  - [x] **Commit ce0baa1** en branch `fase-4-output-rich`
- [x] **Total Fase 4**: 25 tests nuevos, 276 tests totales

### ❌ Faltante (15%)

- [ ] Integración IA opcional con Claude API (Fase 3) - SUSPENDIDA
- [ ] `.pre-commit-hooks.yaml` para framework (Fase 5)
- [ ] Documentación completa de uso (Fase 6)

**Progreso total:** 85% (~42/49.5 horas) → Objetivo: 100%

---

## Fases de Implementación

### Fase 1: Configuración Moderna ✅ COMPLETADA

**Objetivo:** Soportar configuración desde `pyproject.toml` con fallback a `.yml`

#### Ticket 1.1: Agregar soporte para pyproject.toml ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/config.py`
- **Descripción:** Implementar método `from_pyproject_toml()`
- **Criterios de aceptación:**
  - [x] Leer sección `[tool.codeguard]` de pyproject.toml
  - [x] Parsear configuración básica (umbrales, checks habilitados)
  - [x] Parsear subsección `[tool.codeguard.ai]`
  - [x] Parsear `exclude_patterns`
  - [x] Retornar instancia de `CodeGuardConfig`
  - [x] Test unitario que valide lectura correcta (11 tests passing)
- **Estimación:** 2-3 horas
- **Tiempo real:** ~2 horas
- **Fecha completado:** 2026-01-20

#### Ticket 1.2: Implementar búsqueda en orden de prioridad ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/config.py`
- **Descripción:** Función `load_config()` que busca en orden: pyproject.toml → .codeguard.yml → defaults
- **Criterios de aceptación:**
  - [x] Buscar primero en `pyproject.toml` (raíz proyecto)
  - [x] Si no existe o no tiene `[tool.codeguard]`, buscar `.codeguard.yml`
  - [x] Si ninguno existe, usar `CodeGuardConfig()` defaults
  - [x] Logging de qué archivo se usó
  - [x] Test con cada escenario (8 tests agregados, todos pasando)
- **Estimación:** 1-2 horas
- **Tiempo real:** ~1.5 horas
- **Fecha completado:** 2026-01-20

#### Ticket 1.3: Agregar configuración de IA ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/config.py`
- **Descripción:** Agregar dataclass `AIConfig` y campo en `CodeGuardConfig`
- **Criterios de aceptación:**
  - [x] Crear `@dataclass AIConfig` con: `enabled`, `explain_errors`, `suggest_fixes`, `max_tokens`
  - [x] Agregar campo `ai: AIConfig` en `CodeGuardConfig`
  - [x] Defaults: `enabled=False` (opt-in)
  - [x] Parsear desde pyproject.toml subsección `[tool.codeguard.ai]`
  - [x] Tests (incluidos en los 19 tests de Fase 1)
- **Nota:** Completado como parte del Ticket 1.1 para mayor cohesión
- **Fecha completado:** 2026-01-20

**Total Fase 1:** 4-6 horas (completado en ~3.5 horas) ✅

---

### Fase 1.5: Fundamentos de Arquitectura Modular ✅ COMPLETADA

**Objetivo:** Crear infraestructura base para sistema modular con orquestación contextual

**Contexto:** Esta fase implementa la decisión arquitectónica de Feb 2026 (ver `decision_arquitectura_checks_modulares.md`)

#### Ticket 1.5.1: Crear clase base Verifiable ✅ COMPLETADO
- **Archivo:** `src/quality_agents/shared/verifiable.py` (nuevo)
- **Descripción:** Implementar clase base abstracta `Verifiable` y `ExecutionContext`
- **Criterios de aceptación:**
  - [x] Crear dataclass `ExecutionContext` con campos:
    - `file_path: Path`
    - `is_new_file: bool`
    - `is_modified: bool`
    - `analysis_type: str` ("pre-commit", "pr-review", "full")
    - `time_budget: Optional[float]` (segundos disponibles)
    - `config: Any`
    - `is_excluded: bool`
    - `ai_enabled: bool`
  - [x] Crear clase abstracta `Verifiable` con:
    - Properties abstractas: `name`, `category`
    - Properties concretas: `estimated_duration` (default 1.0), `priority` (default 5)
    - Método concreto: `should_run(context) -> bool` (default: not context.is_excluded)
    - Método abstracto: `execute(file_path) -> List[Any]`
  - [x] Documentación completa con docstrings
  - [x] Tests unitarios de la clase base (14 tests)
- **Estimación:** 2-3 horas
- **Tiempo real:** ~2 horas
- **Fecha completado:** 2026-02-03
- **Commit:** cfc0158
- **Archivos creados:** `shared/verifiable.py` (236 líneas)

#### Ticket 1.5.2: Crear CheckOrchestrator ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/orchestrator.py` (nuevo)
- **Descripción:** Implementar orquestador de checks con auto-discovery
- **Criterios de aceptación:**
  - [x] Método `_discover_checks() -> List[Verifiable]` con auto-discovery
    - Buscar en `codeguard.checks` todas las clases que heredan de `Verifiable`
    - Instanciar y retornar lista
  - [x] Método `select_checks(context: ExecutionContext) -> List[Verifiable]`
    - Filtrar checks por `should_run(context)`
    - Aplicar estrategia según `context.analysis_type`
  - [x] Estrategia `_select_for_precommit(candidates, context)`
    - Solo checks rápidos (estimated_duration < 2s)
    - Alta prioridad (priority <= 3)
    - Respetar presupuesto de tiempo (time_budget = 5s)
  - [x] Estrategia `_select_for_pr(candidates, context)`
    - Todos los checks habilitados
  - [x] Ordenar checks por prioridad (1=más alta primero)
  - [x] Tests con mocks de checks (13 tests)
- **Estimación:** 3-4 horas
- **Tiempo real:** ~3 horas
- **Fecha completado:** 2026-02-03
- **Commit:** 9a459ba
- **Archivos creados:** `codeguard/orchestrator.py` (285 líneas)

#### Ticket 1.5.3: Crear estructura de directorios modular ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/checks/` (nuevo directorio)
- **Descripción:** Crear estructura modular de checks
- **Criterios de aceptación:**
  - [x] Crear directorio `codeguard/checks/`
  - [x] Crear `checks/__init__.py` con imports y `__all__`
  - [x] Documentar estructura en docstring de `__init__.py`
- **Estimación:** 0.5 horas
- **Tiempo real:** ~0.5 horas
- **Fecha completado:** 2026-02-03
- **Commit:** 8c0750c

**Total Fase 1.5:** 5.5-7.5 horas (completado en ~5.5 horas) ✅
**Tests agregados:** 27 tests (14 + 13)
**Total tests acumulado:** 71 tests pasando

---

### Fase 2: Migración a Arquitectura Modular ✅ COMPLETADA

**Objetivo:** Migrar checks de funciones a clases modulares heredando de `Verifiable`

**Nota:** Esta fase asumió que Fase 1.5 estaba completada (clase base + orquestador)

#### Ticket 2.1: Migrar check_pep8 a PEP8Check ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/checks/pep8_check.py` (nuevo)
- **Descripción:** Convertir función `check_pep8()` en clase `PEP8Check(Verifiable)`
- **Criterios de aceptación:**
  - [x] Implementación funcional de check_pep8 existe en `checks.py`
  - [x] Crear clase `PEP8Check(Verifiable)` en módulo nuevo
  - [x] Migrar lógica de función a método `execute(file_path)`
  - [x] Implementar `should_run(context)`:
    - Solo archivos `.py`
    - No excluidos
    - `config.check_pep8 = True`
  - [x] Definir properties:
    - `name = "PEP8"`
    - `category = "style"`
    - `estimated_duration = 0.5`
    - `priority = 2` (alta prioridad)
  - [x] Actualizar tests en `test_codeguard_checks.py` para usar clase
  - [x] Exportar en `checks/__init__.py`
  - [x] Deprecar función antigua en `checks.py` (agregar warning)
- **Estimación:** 2 horas
- **Tiempo real:** ~2 horas
- **Fecha completado:** 2026-02-03
- **Commit:** 7334e18
- **Tests:** 15 tests pasando

#### Ticket 2.2: Implementar PylintCheck como clase ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/checks/pylint_check.py` (nuevo)
- **Descripción:** Implementar check de pylint como clase modular
- **Criterios de aceptación:**
  - [x] Crear clase `PylintCheck(Verifiable)`
  - [x] Ejecutar pylint via subprocess con formato parseable
  - [x] Parsear score del output (línea "Your code has been rated X.XX/10")
  - [x] Comparar con `min_score` del config (default 8.0)
  - [x] Crear CheckResult:
    - Severity = WARNING si score < min_score
    - Severity = INFO si score >= min_score
    - Incluir score en mensaje
  - [x] Properties:
    - `name = "Pylint"`
    - `category = "quality"`
    - `estimated_duration = 2.0`
    - `priority = 4` (media prioridad)
  - [x] `should_run()`: solo si `config.check_pylint = True`
  - [x] Tests completos (score alto, score bajo, sin pylint instalado)
  - [x] Exportar en `checks/__init__.py`
- **Estimación:** 2-3 horas
- **Tiempo real:** ~2.5 horas
- **Fecha completado:** 2026-02-03
- **Commit:** 03f229f
- **Tests:** 23 tests pasando

#### Ticket 2.3: Implementar SecurityCheck como clase ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/checks/security_check.py` (nuevo)
- **Descripción:** Implementar check de seguridad con bandit
- **Criterios de aceptación:**
  - [x] Crear clase `SecurityCheck(Verifiable)`
  - [x] Ejecutar bandit con formato JSON (`bandit -f json file.py`)
  - [x] Parsear resultados JSON
  - [x] Mapear severidad:
    - Bandit HIGH → Severity.ERROR
    - Bandit MEDIUM → Severity.WARNING
    - Bandit LOW → Severity.INFO
  - [x] Incluir line_number y descripción de issue
  - [x] Sugerencias específicas por tipo de issue (B201, B301, etc.)
  - [x] Properties:
    - `name = "Security"`
    - `category = "security"`
    - `estimated_duration = 1.5`
    - `priority = 1` (máxima prioridad - seguridad crítica)
  - [x] `should_run()`: solo si `config.check_security = True`
  - [x] Tests con código inseguro:
    - Hardcoded secret
    - `eval()` usage
    - `exec()` usage
    - SQL injection patterns
  - [x] Exportar en `checks/__init__.py`
- **Estimación:** 3 horas
- **Tiempo real:** ~3 horas
- **Fecha completado:** 2026-02-03
- **Commit:** 98f21ea
- **Tests:** 24 tests pasando

#### Ticket 2.4: Implementar ComplexityCheck como clase ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/checks/complexity_check.py` (nuevo)
- **Descripción:** Implementar check de complejidad ciclomática con radon
- **Criterios de aceptación:**
  - [x] Crear clase `ComplexityCheck(Verifiable)`
  - [x] Ejecutar radon cc (`radon cc -s file.py`)
  - [x] Parsear output para extraer funciones con CC > max_cc
  - [x] Crear CheckResult:
    - Severity = INFO (solo informativo, no bloquea)
    - Incluir nombre de función y CC en message
    - Sugerencia: "Consider refactoring into smaller functions"
  - [x] Properties:
    - `name = "Complexity"`
    - `category = "quality"`
    - `estimated_duration = 1.0`
    - `priority = 5` (prioridad media)
  - [x] `should_run()`: solo si `config.check_complexity = True`
  - [x] Tests con función compleja (CC > 10)
  - [x] Exportar en `checks/__init__.py`
- **Estimación:** 2 horas
- **Tiempo real:** ~2 horas
- **Fecha completado:** 2026-02-03
- **Commit:** 12d9b1a
- **Tests:** 27 tests pasando

#### Ticket 2.5: Implementar TypeCheck como clase ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/checks/type_check.py` (nuevo)
- **Descripción:** Implementar check de type errors con mypy
- **Criterios de aceptación:**
  - [x] Crear clase `TypeCheck(Verifiable)`
  - [x] Detectar si archivo tiene type hints (buscar `: ` o `->` en código)
  - [x] Ejecutar mypy solo si tiene hints
  - [x] Parsear errores de tipo
  - [x] Crear CheckResult:
    - Severity = WARNING
    - Incluir line_number y mensaje de error
  - [x] Properties:
    - `name = "Types"`
    - `category = "quality"`
    - `estimated_duration = 3.0`
    - `priority = 5` (prioridad media)
  - [x] `should_run()`:
    - Retornar False si archivo no tiene type hints
    - Retornar False si `config.check_types = False`
  - [x] Tests:
    - Archivo con hints y errores de tipo
    - Archivo con hints sin errores
    - Archivo sin hints (no debe ejecutar mypy)
  - [x] Exportar en `checks/__init__.py`
- **Estimación:** 2-3 horas
- **Tiempo real:** ~3 horas
- **Fecha completado:** 2026-02-03
- **Commit:** 066cfaf
- **Tests:** 35 tests pasando

#### Ticket 2.6: Implementar ImportCheck como clase ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/checks/import_check.py` (nuevo)
- **Descripción:** Implementar check de imports sin uso
- **Criterios de aceptación:**
  - [x] Crear clase `ImportCheck(Verifiable)`
  - [x] Usar pylint para detectar imports sin uso (`pylint --disable=all --enable=unused-import`)
  - [x] Parsear output
  - [x] Crear CheckResult:
    - Severity = WARNING
    - Sugerencia: "Run 'autoflake --remove-unused-variables .' to auto-fix"
  - [x] Properties:
    - `name = "UnusedImports"`
    - `category = "quality"`
    - `estimated_duration = 0.5`
    - `priority = 6` (prioridad baja)
  - [x] `should_run()`: solo si `config.check_imports = True`
  - [x] Tests con imports sin uso
  - [x] Exportar en `checks/__init__.py`
- **Estimación:** 2 horas
- **Tiempo real:** ~2 horas
- **Fecha completado:** 2026-02-03
- **Commit:** f1455d1
- **Tests:** 25 tests pasando

**Total Fase 2:** 13-16 horas (completado en ~14.5 horas) ✅
**Tests agregados:** 149 tests (15+23+24+27+35+25)
**Total tests acumulado:** 220 tests pasando

---

### Fase 2.5: Integración con Orquestador ✅ COMPLETADA

**Objetivo:** Conectar checks modulares con el agente principal usando orquestación contextual

#### Ticket 2.5.1: Integrar orquestador en CodeGuard.run() ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/agent.py`
- **Descripción:** Usar orquestador para seleccionar y ejecutar checks
- **Criterios de aceptación:**
  - [x] Instanciar `CheckOrchestrator(config)` en `__init__()`
  - [x] En `run(file_paths, analysis_type="pre-commit", time_budget=None)`:
    - Para cada archivo:
      - Crear `ExecutionContext` con:
        - `file_path`
        - `analysis_type` (parámetro del método)
        - `time_budget` (parámetro del método)
        - `config`
        - `is_excluded` (verificar con `_is_excluded()`)
        - `ai_enabled = config.ai.enabled`
      - Llamar `orchestrator.select_checks(context)`
      - Ejecutar cada check seleccionado con `check.execute(file_path)`
      - Agregar resultados a `self.results`
  - [x] Agregar manejo de errores:
    - Try/except en cada `check.execute()`
    - Si falla, crear CheckResult con ERROR
    - Continuar con otros checks
  - [x] Logging de checks ejecutados y omitidos
  - [x] Tests de integración:
    - Test con `analysis_type="pre-commit"` (solo checks rápidos)
    - Test con `analysis_type="full"` (todos los checks)
    - Test con archivo excluido (no ejecutar checks)
- **Estimación:** 2-3 horas
- **Tiempo real:** ~2.5 horas
- **Fecha completado:** 2026-02-03
- **Commit:** 85f4c0b
- **Tests:** 15 tests de integración

#### Ticket 2.5.2: Tests de orquestación end-to-end ✅ COMPLETADO
- **Archivo:** `tests/e2e/test_codeguard_e2e.py` (nuevo)
- **Descripción:** Probar flujo completo con múltiples checks y diferentes contextos
- **Criterios de aceptación:**
  - [x] Tests CLI end-to-end (8 tests):
    - CLI básico, formato JSON, configuración pyproject.toml
    - Test de exclusión de archivos
    - Verificación de output correcto
  - [x] Tests de detección real (4 tests):
    - Detección PEP8, complexity, imports, security
    - Verificar que los checks detectan problemas reales
  - [x] Tests de orquestación contextual (2 tests):
    - Pre-commit solo ejecuta checks rápidos
    - Full analysis ejecuta todos los checks
  - [x] Tests con proyecto de ejemplo (2 tests):
    - Análisis completo del ejemplo
    - Sin errores en ejecución
  - [x] Helper `extract_json_from_output()` para parsear salida JSON
- **Estimación:** 2-3 horas
- **Tiempo real:** ~3 horas
- **Fecha completado:** 2026-02-03
- **Commit:** 57602a2
- **Tests:** 16 tests e2e

#### Ticket 2.5.3: Actualizar CLI para soportar analysis_type ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/agent.py` (función `main()`)
- **Descripción:** Agregar opción CLI para tipo de análisis
- **Criterios de aceptación:**
  - [x] Agregar argumento `--analysis-type` con opciones:
    - `pre-commit` (default)
    - `pr-review`
    - `full`
  - [x] Agregar argumento `--time-budget` (float, opcional)
  - [x] Pasar `analysis_type` a `CodeGuard.run()`
  - [x] Pasar `time_budget` a `CodeGuard.run()`
  - [x] Documentar en `--help`
  - [x] Test CLI con diferentes tipos (incluidos en 2.5.2)
- **Estimación:** 1 hora
- **Tiempo real:** ~0.5 horas (implementado en 2.5.1)
- **Fecha completado:** 2026-02-03
- **Commit:** 85f4c0b (mismo que 2.5.1)

**Total Fase 2.5:** 5-7 horas (completado en ~6 horas) ✅
**Tests agregados:** 31 tests (15 integración + 16 e2e)
**Total tests acumulado:** 251 tests pasando (100%)

---

### Fase 3: IA Opcional con Claude 🎯 PRIORIDAD MEDIA

**Objetivo:** Agregar explicaciones inteligentes de errores usando Claude API

**Nota:** Esta fase NO cambia con la arquitectura modular (IA se aplica a resultados agregados)

#### Ticket 3.1: Crear módulo de integración IA
- **Archivo:** `src/quality_agents/codeguard/ai_suggestions.py` (nuevo)
- **Descripción:** Módulo para interactuar con Claude API
- **Criterios de aceptación:**
  - [ ] Función `explain_errors(results: List[CheckResult], config: AIConfig) -> str`
  - [ ] Verificar `ANTHROPIC_API_KEY` en env
  - [ ] Crear prompt con errores detectados
  - [ ] Llamar a Claude API (modelo de config)
  - [ ] Parsear respuesta
  - [ ] Timeout de 3s
  - [ ] Manejo de errores API (rate limit, invalid key, etc.)
  - [ ] Test unitario con mock de API
- **Estimación:** 3-4 horas

#### Ticket 3.2: Integrar IA en flujo de CodeGuard
- **Archivo:** `src/quality_agents/codeguard/agent.py`
- **Descripción:** Llamar IA solo si config.ai.enabled y hay errores
- **Criterios de aceptación:**
  - [ ] Después de ejecutar checks, verificar si hay errores (ERROR o WARNING)
  - [ ] Si NO hay errores → terminar (no llamar IA)
  - [ ] Si hay errores AND config.ai.enabled = True → llamar `explain_errors()`
  - [ ] Agregar explicación IA a output
  - [ ] Si config.ai.enabled = False → no llamar IA
  - [ ] Medir tiempo: debe ser ~2s sin IA, ~4s con IA
  - [ ] Test con IA habilitada/deshabilitada
- **Estimación:** 2 horas

#### Ticket 3.3: Formatear output de IA
- **Archivo:** `src/quality_agents/codeguard/ai_suggestions.py`
- **Descripción:** Formatear respuesta de Claude en formato legible
- **Criterios de aceptación:**
  - [ ] Parsear markdown de respuesta
  - [ ] Separar explicación de sugerencias
  - [ ] Formatear para consola con Rich
  - [ ] Limitar a `max_tokens` de config
  - [ ] Test con respuesta de ejemplo
- **Estimación:** 2 horas

**Total Fase 3:** 7-8 horas

---

### Fase 4: Output Formateado con Rich ✅ COMPLETADA

**Objetivo:** Salida visual profesional en consola

#### Ticket 4.1: Implementar formatter con Rich ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/formatter.py` (nuevo)
- **Descripción:** Crear módulo para formatear output con Rich
- **Criterios de aceptación:**
  - [x] Función `format_results(results: List[CheckResult], elapsed: float) -> None`
  - [x] Usar Rich Console, Panel, Table
  - [x] Header con logo/nombre
  - [x] Resultados agrupados por severidad (ERROR, WARN, INFO)
  - [x] Colores: rojo=ERROR, amarillo=WARN, azul=INFO, verde=PASS
  - [x] Summary con contadores
  - [x] Tiempo de ejecución
  - [x] Sugerencias al final (contextuales: black, autoflake, security, etc.)
  - [x] 18 tests unitarios
- **Estimación:** 3-4 horas
- **Tiempo real:** ~3 horas
- **Fecha completado:** 2026-02-04
- **Commit:** 1aed60c

#### Ticket 4.2: Agregar modo JSON ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/formatter.py`
- **Descripción:** Mejorar formato JSON con estructura completa
- **Criterios de aceptación:**
  - [x] Función `format_json(results: List[CheckResult]) -> str`
  - [x] Serializar CheckResult a dict
  - [x] Estructura con summary, results, by_severity
  - [x] Timestamp ISO, estadísticas completas
  - [x] JSON pretty-printed con ensure_ascii=False
  - [x] 7 tests unitarios
- **Estimación:** 1-2 horas
- **Tiempo real:** ~1.5 horas
- **Fecha completado:** 2026-02-04
- **Commit:** d5b1c44

#### Ticket 4.3: Integrar formatter en agent.py ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/agent.py`
- **Descripción:** Usar formatters en CLI según opción
- **Criterios de aceptación:**
  - [x] Import de `format_results` y `format_json`
  - [x] Medición de tiempo de ejecución (import time)
  - [x] Si `text` → usar Rich formatter con parámetros completos
  - [x] Si `json` → usar JSON formatter
  - [x] Output limpio: mensajes solo en modo text
  - [x] Eliminadas funciones antiguas (_display_results_*)
  - [x] Tests e2e actualizados para nuevo formato JSON (16 tests)
- **Estimación:** 1 hora
- **Tiempo real:** ~1 hora
- **Fecha completado:** 2026-02-04
- **Commit:** ce0baa1

**Total Fase 4:** 5-7 horas (completado en ~5.5 horas) ✅
**Tests agregados:** 25 tests (18 + 7 nuevos formatter)
**Total tests acumulado:** 276 tests pasando (100%)

---

### Fase 5: Soporte para pre-commit Framework 🎯 PRIORIDAD MEDIA

**Objetivo:** Habilitar uso con pre-commit framework

#### Ticket 5.1: Crear .pre-commit-hooks.yaml
- **Archivo:** `.pre-commit-hooks.yaml` (raíz del repositorio)
- **Descripción:** Definir hook para pre-commit framework
- **Criterios de aceptación:**
  - [ ] ID: `codeguard`
  - [ ] Name: "CodeGuard Quality Check"
  - [ ] Entry: `codeguard --analysis-type pre-commit`
  - [ ] Language: `python`
  - [ ] Pass filenames: `false` (analiza todo el proyecto)
  - [ ] Files: `\.py$`
  - [ ] Always run: `false`
  - [ ] Test integrando en proyecto externo
- **Estimación:** 1 hora

#### Ticket 5.2: Documentar uso con pre-commit
- **Archivo:** `README.md` o `docs/guias/codeguard.md`
- **Descripción:** Agregar sección de integración con pre-commit
- **Criterios de aceptación:**
  - [ ] Ejemplo de `.pre-commit-config.yaml`
  - [ ] Comandos de instalación
  - [ ] Cómo ejecutar manualmente
  - [ ] Troubleshooting común
- **Estimación:** 1 hora

**Total Fase 5:** 2 horas

---

### Fase 6: Tests y Documentación 🎯 PRIORIDAD MEDIA

**Objetivo:** Asegurar calidad y usabilidad

#### Ticket 6.1: Tests de integración end-to-end completos
- **Archivo:** `tests/integration/test_codeguard_integration.py`
- **Descripción:** Test completo de flujo con arquitectura modular
- **Criterios de aceptación:**
  - [ ] Crear proyecto temporal con código de ejemplo
  - [ ] Ejecutar codeguard sobre el proyecto
  - [ ] Verificar que detecta errores esperados
  - [ ] Verificar tiempo < 5s en pre-commit
  - [ ] Test con IA habilitada/deshabilitada
  - [ ] Test con configuración desde pyproject.toml
  - [ ] Test con configuración desde .yml
  - [ ] Test sin configuración (defaults)
  - [ ] Test de orquestación (verificar qué checks se ejecutaron)
- **Estimación:** 3-4 horas

#### Ticket 6.2: Actualizar README.md
- **Archivo:** `README.md`
- **Descripción:** Documentar instalación y uso básico de CodeGuard
- **Criterios de aceptación:**
  - [ ] Sección de instalación
  - [ ] Ejemplos de uso (4 modelos de integración)
  - [ ] Configuración básica
  - [ ] Configuración de IA
  - [ ] FAQ
  - [ ] Screenshots o ejemplos de output
  - [ ] Mencionar arquitectura modular (para contribuidores)
- **Estimación:** 2-3 horas

#### Ticket 6.3: Crear ejemplo funcional
- **Archivo:** `examples/sample_project/` (actualizar)
- **Descripción:** Proyecto de ejemplo con CodeGuard configurado
- **Criterios de aceptación:**
  - [ ] Código Python con algunos problemas de calidad
  - [ ] `pyproject.toml` con configuración de CodeGuard
  - [ ] `.pre-commit-config.yaml` configurado
  - [ ] README explicando el ejemplo
  - [ ] Script para probarlo
- **Estimación:** 2 horas

**Total Fase 6:** 7-9 horas

---

## Resumen de Estimaciones

| Fase | Descripción | Horas Estimadas | Horas Reales | Prioridad | Estado |
|------|-------------|-----------------|--------------|-----------|--------|
| 1 | Configuración moderna (pyproject.toml) | 4-6 | ~3.5 | CRÍTICA | ✅ COMPLETADA |
| 1.5 | Fundamentos de arquitectura modular | 5.5-7.5 | ~5.5 | CRÍTICA | ✅ COMPLETADA |
| 2 | Migración a arquitectura modular | 13-16 | ~14.5 | ALTA | ✅ COMPLETADA |
| 2.5 | Integración con orquestador | 5-7 | ~6 | ALTA | ✅ COMPLETADA |
| 3 | IA opcional con Claude | 7-8 | - | MEDIA | 🚫 SUSPENDIDA |
| 4 | Output formateado con Rich | 5-7 | ~5.5 | MEDIA | ✅ COMPLETADA |
| 5 | Soporte pre-commit framework | 2 | - | MEDIA | ⏳ PENDIENTE |
| 6 | Tests y documentación | 7-9 | - | MEDIA | ⏳ PENDIENTE |
| **TOTAL** | **MVP Funcional con Arquitectura Modular** | **49-67.5 horas** | **~35h / 42-59.5h** | - | **85% completo** |

**Progreso:**
- ✅ **Completado:** Fases 1, 1.5, 2, 2.5, 4 (~35 horas)
- 🚫 **Suspendida:** Fase 3 (IA opcional)
- ⏳ **Pendiente:** Fases 5, 6 (~9-11 horas restantes)

**Incremento vs plan original:** +11-13.5 horas por arquitectura modular
**Justificación:** Inversión en calidad arquitectónica, extensibilidad y mantenibilidad

**Estimación conservadora restante:** 2.5-5 días de trabajo (8h/día)

---

## Orden Recomendado de Ejecución

Para maximizar valor incremental con arquitectura modular:

### Sprint 1 (Prioridad CRÍTICA-ALTA): Fases 1.5, 2, 2.5 ✅ COMPLETADO
- **Objetivo:** Sistema modular funcional con checks reales
- **Resultado:** CodeGuard con arquitectura modular + 6 checks + orquestación ✅
- **Horas estimadas:** ~24-30.5 horas
- **Horas reales:** ~26 horas
- **Valor entregado:** Base arquitectónica sólida, 251 tests pasando, sistema completamente funcional
- **Fecha completado:** 2026-02-03

### Sprint 2 (Prioridad MEDIA): Fases 3, 4 ⏳ PRÓXIMO
- **Objetivo:** IA opcional + output profesional
- **Resultado:** Explicaciones inteligentes + salida formateada
- **Horas:** ~12-15 horas
- **Valor:** Experiencia de usuario profesional

### Sprint 3 (Finalización): Fases 5, 6
- **Objetivo:** Integración completa + documentación
- **Resultado:** Framework listo para producción
- **Horas:** ~9-11 horas
- **Valor:** Adopción y usabilidad

---

## Criterios de Éxito del MVP

CodeGuard estará listo cuando:

**Funcionalidad:**
- [x] Se instala con `pip install -e ".[dev]"` ✅
- [x] Comando `codeguard .` funciona ✅
- [x] Lee configuración desde `pyproject.toml` o `.yml` ✅
- [x] Ejecuta los 6 checks de calidad correctamente **como clases modulares** ✅
- [x] **Orquestador selecciona checks contextualmente** ✅
- [x] Termina en < 5 segundos en pre-commit ✅
- [ ] Termina en ~4s con errores + IA habilitada (Fase 3)
- [ ] IA opcional funciona cuando se habilita (Fase 3)
- [ ] Output en consola es legible y profesional (Fase 4)
- [ ] Soporta pre-commit framework (Fase 5)

**Arquitectura:**
- [x] **Clase base `Verifiable` funcional** ✅
- [x] **CheckOrchestrator con auto-discovery** ✅
- [x] **6 checks como clases independientes** ✅
- [x] Fácil agregar nuevos checks (crear clase + exportar) ✅

**Calidad:**
- [x] Tiene al menos 80% de cobertura de tests ✅ (251 tests pasando)
- [x] Tests de orquestación pasando ✅ (31 tests integración/e2e)
- [ ] README documenta uso básico y arquitectura (Fase 6)
- [x] Ejemplo funcional en `examples/` ✅

**Progreso:** 13/18 criterios cumplidos (72%) - Sistema core completamente funcional

---

## Registro de Progreso

### 2026-01-20: Plan creado
- [x] Análisis de estado actual
- [x] Definición de fases y tickets
- [x] Estimaciones de esfuerzo

### 2026-01-20: Fase 1 completada ✅
- [x] Ticket 1.1: Soporte pyproject.toml (~2h)
- [x] Ticket 1.2: Búsqueda automática de config (~1.5h)
- [x] Ticket 1.3: Configuración de IA (merged con 1.1)
- [x] 19 tests unitarios pasando

**Cambios realizados:**
- `src/quality_agents/codeguard/config.py`: +130 líneas
- `tests/unit/test_codeguard_config.py`: Nuevo archivo, 250 líneas, 19 tests
- `pyproject.toml`: +1 dependencia (tomli)

### 2026-02-02: Ticket 2.1 completado (implementación funcional) ✅
- [x] Implementada función `check_pep8()` con ejecución de flake8
- [x] Parseo de output con extracción de línea, columna y mensaje
- [x] Manejo de errores (FileNotFoundError, TimeoutExpired, Exception)
- [x] Severity = WARNING para violaciones
- [x] Sugerencia de auto-formateo con black
- [x] Creados 4 tests unitarios en `test_codeguard_checks.py`
- [x] Todos los tests pasando ✅

**Cambios realizados:**
- `src/quality_agents/codeguard/checks.py`: +74 líneas (función check_pep8)
- `tests/unit/test_codeguard_checks.py`: Nuevo archivo, 151 líneas, 4 tests

### 2026-02-02: Decisión arquitectónica - Arquitectura Modular ⚠️
- [x] Documento `decision_arquitectura_checks_modulares.md` creado
- [x] Análisis de impacto en `analisis_impacto_arquitectura_modular.md`
- [x] Plan rediseñado con nuevas fases 1.5 y 2.5

**Cambios en plan:**
- Nueva Fase 1.5: Fundamentos de arquitectura modular (+5.5-7.5h)
- Fase 2 rediseñada: Migración a clases modulares (13-16h sin cambio)
- Nueva Fase 2.5: Integración con orquestador (+5-7h)
- **Total incrementado:** 49-67.5h (vs 42-54h original)

**Justificación del incremento:**
- Inversión en arquitectura que paga dividendos en mantenibilidad
- Facilita agregar nuevos checks (create class + export = done)
- Decisiones contextuales (pre-commit vs full analysis)
- Preparado para IA en orquestación
- Alineado con principios fundamentales del proyecto

### 2026-02-03: Fase 1.5 completada ✅
- [x] Ticket 1.5.1: Clase base Verifiable + ExecutionContext (~2h) - Commit cfc0158
- [x] Ticket 1.5.2: CheckOrchestrator con auto-discovery (~3h) - Commit 9a459ba
- [x] Ticket 1.5.3: Estructura de directorios modular (~0.5h) - Commit 8c0750c
- [x] 27 tests nuevos (14 + 13), total 71 tests pasando

**Cambios realizados:**
- `src/quality_agents/shared/verifiable.py`: Nuevo archivo, 236 líneas
- `src/quality_agents/codeguard/orchestrator.py`: Nuevo archivo, 285 líneas
- `src/quality_agents/codeguard/checks/__init__.py`: Nuevo archivo
- `tests/unit/test_verifiable.py`: Nuevo archivo, 14 tests
- `tests/unit/test_orchestrator.py`: Nuevo archivo, 13 tests

### 2026-02-03: Fase 2 completada ✅
- [x] Ticket 2.1: PEP8Check (~2h) - Commit 7334e18 - 15 tests
- [x] Ticket 2.2: PylintCheck (~2.5h) - Commit 03f229f - 23 tests
- [x] Ticket 2.3: SecurityCheck (~3h) - Commit 98f21ea - 24 tests
- [x] Ticket 2.4: ComplexityCheck (~2h) - Commit 12d9b1a - 27 tests
- [x] Ticket 2.5: TypeCheck (~3h) - Commit 066cfaf - 35 tests
- [x] Ticket 2.6: ImportCheck (~2h) - Commit f1455d1 - 25 tests
- [x] 6/6 checks implementados como clases modulares
- [x] 149 tests nuevos, total 220 tests pasando

**Cambios realizados:**
- `src/quality_agents/codeguard/checks/pep8_check.py`: Nuevo archivo
- `src/quality_agents/codeguard/checks/pylint_check.py`: Nuevo archivo
- `src/quality_agents/codeguard/checks/security_check.py`: Nuevo archivo
- `src/quality_agents/codeguard/checks/complexity_check.py`: Nuevo archivo
- `src/quality_agents/codeguard/checks/type_check.py`: Nuevo archivo
- `src/quality_agents/codeguard/checks/import_check.py`: Nuevo archivo
- Todos los checks exportados en `checks/__init__.py`
- Tests en `tests/unit/test_codeguard_checks.py`

### 2026-02-03: Fase 2.5 completada ✅
- [x] Ticket 2.5.1: Integrar orquestador en CodeGuard.run() (~2.5h) - Commit 85f4c0b - 15 tests
- [x] Ticket 2.5.2: Tests de orquestación end-to-end (~3h) - Commit 57602a2 - 16 tests
- [x] Ticket 2.5.3: CLI con --analysis-type (~0.5h) - Commit 85f4c0b
- [x] 31 tests nuevos (15 integración + 16 e2e), total 251 tests pasando (100%)

**Cambios realizados:**
- `src/quality_agents/codeguard/agent.py`: Integración completa con orquestador
  - Método `run()` reescrito con orquestación contextual
  - CLI actualizado con `--analysis-type` y `--time-budget`
  - Creación de `ExecutionContext` por archivo
  - Manejo robusto de errores
- `tests/integration/test_codeguard_integration.py`: 15 tests de integración
- `tests/e2e/test_codeguard_e2e.py`: Nuevo archivo, 16 tests e2e
  - 4 categorías: CLI, detección real, orquestación, ejemplo

**Estado final:**
- ✅ CodeGuard completamente funcional con arquitectura modular
- ✅ 6 checks modulares operativos
- ✅ Orquestación contextual funcionando (pre-commit, pr-review, full)
- ✅ CLI completo con todas las opciones
- ✅ 251/251 tests pasando (100%)
- ✅ Listo para uso en pre-commit hooks
- ⏳ Pendiente: IA opcional (Fase 3 - suspendida), Output Rich (Fase 4)

### 2026-02-04: Fase 4 completada ✅
- [x] Ticket 4.1: Implementar formatter con Rich (~3h) - Commit 1aed60c - 18 tests
- [x] Ticket 4.2: Agregar modo JSON mejorado (~1.5h) - Commit d5b1c44 - 7 tests
- [x] Ticket 4.3: Integrar formatter en agent.py (~1h) - Commit ce0baa1
- [x] 25 tests nuevos (18 + 7), total 276 tests pasando (100%)

**Cambios realizados:**
- `src/quality_agents/codeguard/formatter.py`: Nuevo archivo, 325 líneas
  - Función `format_results()` con Rich (Console, Panel, Table)
  - Header con logo, estadísticas, tablas por severidad, sugerencias
  - Función `format_json()` con estructura completa (summary, results, by_severity)
  - Timestamp ISO, pretty-printed, ensure_ascii=False
- `src/quality_agents/codeguard/agent.py`: Modificado
  - Import de formatters desde formatter.py
  - Medición de tiempo de ejecución
  - Eliminadas funciones antiguas _display_results_*
  - Output limpio según formato (text/json)
- `tests/unit/test_formatter.py`: Nuevo archivo, 453 líneas, 25 tests
- `tests/e2e/test_codeguard_e2e.py`: Actualizado para nuevo formato JSON

**Estado final:**
- ✅ Output profesional con Rich (colores, tablas, sugerencias)
- ✅ JSON con metadata completa y agrupación por severidad
- ✅ CLI completamente funcional: `codeguard . --format text/json`
- ✅ 276/276 tests pasando (100%)
- ✅ Listo para uso en producción
- ⏳ Pendiente: Fase 5 (pre-commit hooks), Fase 6 (documentación)

**Próximo:** Fase 5 - Soporte pre-commit framework (~2h)

---

## Notas Técnicas

### Dependencias

En `pyproject.toml`:

```toml
dependencies = [
    # ... existentes
    "anthropic>=0.8.0",  # IA (ya está)
    "rich>=13.7.0",      # Output (ya está)
    "tomli>=2.0.0; python_version < '3.11'",  # ✅ Leer pyproject.toml (ya está)
]
```

Flake8, Pylint, Bandit, Radon ya están como dependencias. Verificar que estén en `pyproject.toml`.

### Estructura de Archivos Nueva

```
codeguard/
├── agent.py              # CodeGuard principal + CLI
├── config.py             # Configuración ✅
├── orchestrator.py       # Orquestador (NUEVO - Fase 1.5)
├── checks/               # Checks modulares (NUEVO - Fase 1.5+2)
│   ├── __init__.py       # Exports
│   ├── pep8_check.py     # PEP8Check(Verifiable)
│   ├── pylint_check.py   # PylintCheck(Verifiable)
│   ├── security_check.py # SecurityCheck(Verifiable)
│   ├── complexity_check.py  # ComplexityCheck(Verifiable)
│   ├── types_check.py    # TypesCheck(Verifiable)
│   └── imports_check.py  # ImportsCheck(Verifiable)
├── ai_suggestions.py     # Integración IA (Fase 3)
├── formatter.py          # Output Rich (Fase 4)
└── PLAN_IMPLEMENTACION.md  # Este archivo

shared/
├── verifiable.py         # Clase base Verifiable + ExecutionContext (NUEVO - Fase 1.5)
└── ...
```

### Patrón de Implementación de Checks

Cada check sigue este patrón:

```python
from pathlib import Path
from typing import List

from quality_agents.shared.verifiable import Verifiable, ExecutionContext
from quality_agents.codeguard.agent import CheckResult, Severity


class MiCheck(Verifiable):
    """Descripción del check."""

    @property
    def name(self) -> str:
        return "MiCheck"

    @property
    def category(self) -> str:
        return "quality"  # o "style", "security"

    @property
    def estimated_duration(self) -> float:
        return 1.5  # segundos estimados

    @property
    def priority(self) -> int:
        return 3  # 1=alta, 10=baja

    def should_run(self, context: ExecutionContext) -> bool:
        """Decide si debe ejecutarse en este contexto."""
        if context.is_excluded:
            return False
        # Lógica adicional...
        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        """Ejecuta la verificación."""
        results = []
        # Implementación...
        return results
```

---

**Última actualización:** 2026-02-04 (Fases 1.5, 2, 2.5 y 4 Completadas)
**Estado actual:** 85% completo - CodeGuard con arquitectura modular + Rich formatter
**Próximo milestone:** Fase 5 - Soporte pre-commit framework (~2h)
