# Plan de Implementación - CodeGuard

**Fecha de creación:** 2026-01-20
**Última actualización:** 2026-02-02 (Rediseño Arquitectónico)
**Estado:** En Progreso
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

### ✅ Implementado (30%)

- [x] Estructura básica de clases (`CodeGuard`, `CheckResult`, `Severity`)
- [x] CLI con click (`agent.py:main()`)
- [x] Método `collect_files()` funcional
- [x] Dataclass `CodeGuardConfig` para configuración
- [x] Carga desde YAML (método `from_yaml()`)
- [x] **Carga desde `pyproject.toml` (método `from_pyproject_toml()`)** ✅ FASE 1
- [x] **Función `load_config()` con búsqueda automática** ✅ FASE 1
- [x] **Configuración de IA en `AIConfig`** ✅ FASE 1
- [x] Entry point en `pyproject.toml` (`codeguard` command)
- [x] Tests unitarios de configuración (19 tests pasando)
- [x] **Implementación funcional de `check_pep8()`** ✅ TICKET 2.1

### ⏳ En Progreso (5%)

- [ ] **Arquitectura modular** (Fase 1.5 - iniciando)
  - [ ] Clase base `Verifiable`
  - [ ] `CheckOrchestrator`
  - [ ] Migración de checks a clases

### ❌ Faltante (65%)

- [ ] Implementación modular de 5 checks restantes
- [ ] Integración con orquestador
- [ ] Integración IA opcional con Claude API
- [ ] Output formateado con Rich
- [ ] `.pre-commit-hooks.yaml` para framework
- [ ] Tests de integración con orquestación
- [ ] Documentación de uso

**Progreso total:** ~30% → Objetivo: 100%

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

### Fase 1.5: Fundamentos de Arquitectura Modular 🎯 PRIORIDAD CRÍTICA

**Objetivo:** Crear infraestructura base para sistema modular con orquestación contextual

**Contexto:** Esta fase implementa la decisión arquitectónica de Feb 2026 (ver `decision_arquitectura_checks_modulares.md`)

#### Ticket 1.5.1: Crear clase base Verifiable
- **Archivo:** `src/quality_agents/shared/verifiable.py` (nuevo)
- **Descripción:** Implementar clase base abstracta `Verifiable` y `ExecutionContext`
- **Criterios de aceptación:**
  - [ ] Crear dataclass `ExecutionContext` con campos:
    - `file_path: Path`
    - `is_new_file: bool`
    - `is_modified: bool`
    - `analysis_type: str` ("pre-commit", "pr-review", "full")
    - `time_budget: Optional[float]` (segundos disponibles)
    - `config: Any`
    - `is_excluded: bool`
    - `ai_enabled: bool`
  - [ ] Crear clase abstracta `Verifiable` con:
    - Properties abstractas: `name`, `category`
    - Properties concretas: `estimated_duration` (default 1.0), `priority` (default 5)
    - Método concreto: `should_run(context) -> bool` (default: not context.is_excluded)
    - Método abstracto: `execute(file_path) -> List[Any]`
  - [ ] Documentación completa con docstrings
  - [ ] Tests unitarios de la clase base
- **Estimación:** 2-3 horas

#### Ticket 1.5.2: Crear CheckOrchestrator
- **Archivo:** `src/quality_agents/codeguard/orchestrator.py` (nuevo)
- **Descripción:** Implementar orquestador de checks con auto-discovery
- **Criterios de aceptación:**
  - [ ] Método `_discover_checks() -> List[Verifiable]` con auto-discovery
    - Buscar en `codeguard.checks` todas las clases que heredan de `Verifiable`
    - Instanciar y retornar lista
  - [ ] Método `select_checks(context: ExecutionContext) -> List[Verifiable]`
    - Filtrar checks por `should_run(context)`
    - Aplicar estrategia según `context.analysis_type`
  - [ ] Estrategia `_select_for_precommit(candidates, context)`
    - Solo checks rápidos (estimated_duration < 2s)
    - Alta prioridad (priority <= 3)
    - Respetar presupuesto de tiempo (time_budget = 5s)
  - [ ] Estrategia `_select_for_pr(candidates, context)`
    - Todos los checks habilitados
  - [ ] Ordenar checks por prioridad (1=más alta primero)
  - [ ] Tests con mocks de checks
- **Estimación:** 3-4 horas

#### Ticket 1.5.3: Crear estructura de directorios modular
- **Archivo:** `src/quality_agents/codeguard/checks/` (nuevo directorio)
- **Descripción:** Crear estructura modular de checks
- **Criterios de aceptación:**
  - [ ] Crear directorio `codeguard/checks/`
  - [ ] Crear `checks/__init__.py` con imports y `__all__`
  - [ ] Documentar estructura en docstring de `__init__.py`
- **Estimación:** 0.5 horas

**Total Fase 1.5:** 5.5-7.5 horas

---

### Fase 2: Migración a Arquitectura Modular 🎯 PRIORIDAD ALTA

**Objetivo:** Migrar checks de funciones a clases modulares heredando de `Verifiable`

**Nota:** Esta fase asume que Fase 1.5 está completada (clase base + orquestador)

#### Ticket 2.1: Migrar check_pep8 a PEP8Check 🔄 PARCIALMENTE COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/checks/pep8_check.py` (nuevo)
- **Descripción:** Convertir función `check_pep8()` en clase `PEP8Check(Verifiable)`
- **Criterios de aceptación:**
  - [x] Implementación funcional de check_pep8 existe en `checks.py`
  - [ ] Crear clase `PEP8Check(Verifiable)` en módulo nuevo
  - [ ] Migrar lógica de función a método `execute(file_path)`
  - [ ] Implementar `should_run(context)`:
    - Solo archivos `.py`
    - No excluidos
    - `config.check_pep8 = True`
  - [ ] Definir properties:
    - `name = "PEP8"`
    - `category = "style"`
    - `estimated_duration = 0.5`
    - `priority = 2` (alta prioridad)
  - [ ] Actualizar tests en `test_codeguard_checks.py` para usar clase
  - [ ] Exportar en `checks/__init__.py`
  - [ ] Deprecar función antigua en `checks.py` (agregar warning)
- **Estimación:** 2 horas (reducido porque ya existe implementación)
- **Nota:** La lógica de ejecución de flake8 ya está implementada, solo migrar a clase

#### Ticket 2.2: Implementar PylintCheck como clase
- **Archivo:** `src/quality_agents/codeguard/checks/pylint_check.py` (nuevo)
- **Descripción:** Implementar check de pylint como clase modular
- **Criterios de aceptación:**
  - [ ] Crear clase `PylintCheck(Verifiable)`
  - [ ] Ejecutar pylint via subprocess con formato parseable
  - [ ] Parsear score del output (línea "Your code has been rated X.XX/10")
  - [ ] Comparar con `min_score` del config (default 8.0)
  - [ ] Crear CheckResult:
    - Severity = WARNING si score < min_score
    - Severity = INFO si score >= min_score
    - Incluir score en mensaje
  - [ ] Properties:
    - `name = "Pylint"`
    - `category = "quality"`
    - `estimated_duration = 2.0`
    - `priority = 4` (media prioridad)
  - [ ] `should_run()`: solo si `config.check_pylint = True`
  - [ ] Tests completos (score alto, score bajo, sin pylint instalado)
  - [ ] Exportar en `checks/__init__.py`
- **Estimación:** 2-3 horas

#### Ticket 2.3: Implementar SecurityCheck como clase
- **Archivo:** `src/quality_agents/codeguard/checks/security_check.py` (nuevo)
- **Descripción:** Implementar check de seguridad con bandit
- **Criterios de aceptación:**
  - [ ] Crear clase `SecurityCheck(Verifiable)`
  - [ ] Ejecutar bandit con formato JSON (`bandit -f json file.py`)
  - [ ] Parsear resultados JSON
  - [ ] Mapear severidad:
    - Bandit HIGH → Severity.ERROR
    - Bandit MEDIUM → Severity.WARNING
    - Bandit LOW → Severity.INFO
  - [ ] Incluir line_number y descripción de issue
  - [ ] Sugerencias específicas por tipo de issue (B201, B301, etc.)
  - [ ] Properties:
    - `name = "Security"`
    - `category = "security"`
    - `estimated_duration = 1.5`
    - `priority = 1` (máxima prioridad - seguridad crítica)
  - [ ] `should_run()`: solo si `config.check_security = True`
  - [ ] Tests con código inseguro:
    - Hardcoded secret
    - `eval()` usage
    - `exec()` usage
    - SQL injection patterns
  - [ ] Exportar en `checks/__init__.py`
- **Estimación:** 3 horas

#### Ticket 2.4: Implementar ComplexityCheck como clase
- **Archivo:** `src/quality_agents/codeguard/checks/complexity_check.py` (nuevo)
- **Descripción:** Implementar check de complejidad ciclomática con radon
- **Criterios de aceptación:**
  - [ ] Crear clase `ComplexityCheck(Verifiable)`
  - [ ] Ejecutar radon cc (`radon cc -s file.py`)
  - [ ] Parsear output para extraer funciones con CC > max_cc
  - [ ] Crear CheckResult:
    - Severity = INFO (solo informativo, no bloquea)
    - Incluir nombre de función y CC en message
    - Sugerencia: "Consider refactoring into smaller functions"
  - [ ] Properties:
    - `name = "Complexity"`
    - `category = "quality"`
    - `estimated_duration = 1.0`
    - `priority = 5` (prioridad media)
  - [ ] `should_run()`: solo si `config.check_complexity = True`
  - [ ] Tests con función compleja (CC > 10)
  - [ ] Exportar en `checks/__init__.py`
- **Estimación:** 2 horas

#### Ticket 2.5: Implementar TypesCheck como clase
- **Archivo:** `src/quality_agents/codeguard/checks/types_check.py` (nuevo)
- **Descripción:** Implementar check de type errors con mypy
- **Criterios de aceptación:**
  - [ ] Crear clase `TypesCheck(Verifiable)`
  - [ ] Detectar si archivo tiene type hints (buscar `: ` o `->` en código)
  - [ ] Ejecutar mypy solo si tiene hints
  - [ ] Parsear errores de tipo
  - [ ] Crear CheckResult:
    - Severity = WARNING
    - Incluir line_number y mensaje de error
  - [ ] Properties:
    - `name = "Types"`
    - `category = "quality"`
    - `estimated_duration = 2.0`
    - `priority = 6` (prioridad baja - opcional)
  - [ ] `should_run()`:
    - Retornar False si archivo no tiene type hints
    - Retornar False si `config.check_types = False`
  - [ ] Tests:
    - Archivo con hints y errores de tipo
    - Archivo con hints sin errores
    - Archivo sin hints (no debe ejecutar mypy)
  - [ ] Exportar en `checks/__init__.py`
- **Estimación:** 2-3 horas

#### Ticket 2.6: Implementar ImportsCheck como clase
- **Archivo:** `src/quality_agents/codeguard/checks/imports_check.py` (nuevo)
- **Descripción:** Implementar check de imports sin uso
- **Criterios de aceptación:**
  - [ ] Crear clase `ImportsCheck(Verifiable)`
  - [ ] Usar pylint para detectar imports sin uso (`pylint --disable=all --enable=unused-import`)
  - [ ] Parsear output
  - [ ] Crear CheckResult:
    - Severity = WARNING
    - Sugerencia: "Run 'autoflake --remove-unused-variables .' to auto-fix"
  - [ ] Properties:
    - `name = "UnusedImports"`
    - `category = "quality"`
    - `estimated_duration = 1.0`
    - `priority = 3` (prioridad alta - código limpio)
  - [ ] `should_run()`: solo si `config.check_imports = True`
  - [ ] Tests con imports sin uso
  - [ ] Exportar en `checks/__init__.py`
- **Estimación:** 2 horas

**Total Fase 2:** 13-16 horas

---

### Fase 2.5: Integración con Orquestador 🎯 PRIORIDAD ALTA

**Objetivo:** Conectar checks modulares con el agente principal usando orquestación contextual

#### Ticket 2.5.1: Integrar orquestador en CodeGuard.run()
- **Archivo:** `src/quality_agents/codeguard/agent.py`
- **Descripción:** Usar orquestador para seleccionar y ejecutar checks
- **Criterios de aceptación:**
  - [ ] Instanciar `CheckOrchestrator(config)` en `__init__()`
  - [ ] En `run(file_paths, analysis_type="full")`:
    - Para cada archivo:
      - Crear `ExecutionContext` con:
        - `file_path`
        - `analysis_type` (parámetro del método)
        - `time_budget` (5.0 si "pre-commit", None para otros)
        - `config`
        - `is_excluded` (verificar con `_is_excluded()`)
        - `ai_enabled = config.ai.enabled`
      - Llamar `orchestrator.select_checks(context)`
      - Ejecutar cada check seleccionado con `check.execute(file_path)`
      - Agregar resultados a `self.results`
  - [ ] Agregar manejo de errores:
    - Try/except en cada `check.execute()`
    - Si falla, crear CheckResult con ERROR
    - Continuar con otros checks
  - [ ] Logging de checks ejecutados y omitidos
  - [ ] Tests de integración:
    - Test con `analysis_type="pre-commit"` (solo checks rápidos)
    - Test con `analysis_type="full"` (todos los checks)
    - Test con archivo excluido (no ejecutar checks)
- **Estimación:** 2-3 horas

#### Ticket 2.5.2: Tests de orquestación end-to-end
- **Archivo:** `tests/integration/test_codeguard_orchestration.py` (nuevo)
- **Descripción:** Probar flujo completo con múltiples checks y diferentes contextos
- **Criterios de aceptación:**
  - [ ] Test pre-commit con presupuesto de tiempo:
    - Crear archivo con violaciones
    - Ejecutar con `analysis_type="pre-commit"`
    - Verificar que solo ejecuta checks rápidos (PEP8, Security, UnusedImports)
    - Verificar que omite checks lentos (Pylint, Types)
    - Verificar tiempo total < 5s
  - [ ] Test full analysis:
    - Ejecutar con `analysis_type="full"`
    - Verificar que ejecuta todos los checks habilitados
  - [ ] Test con diferentes tipos de archivos:
    - Archivo .py → ejecuta checks
    - Archivo .txt → no ejecuta checks
    - Archivo excluido → no ejecuta checks
  - [ ] Test con presupuesto limitado:
    - `time_budget=2.0`
    - Verificar que solo ejecuta checks que caben en presupuesto
  - [ ] Test de priorización:
    - Verificar orden de ejecución (priority 1, 2, 3... 6)
  - [ ] Test con error en un check:
    - Simular check que falla
    - Verificar que continúa con otros checks
- **Estimación:** 2-3 horas

#### Ticket 2.5.3: Actualizar CLI para soportar analysis_type
- **Archivo:** `src/quality_agents/codeguard/agent.py` (función `main()`)
- **Descripción:** Agregar opción CLI para tipo de análisis
- **Criterios de aceptación:**
  - [ ] Agregar argumento `--analysis-type` con opciones:
    - `pre-commit` (default para uso con pre-commit hook)
    - `pr-review`
    - `full`
  - [ ] Pasar `analysis_type` a `CodeGuard.run()`
  - [ ] Documentar en `--help`
  - [ ] Test CLI con diferentes tipos
- **Estimación:** 1 hora

**Total Fase 2.5:** 5-7 horas

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

### Fase 4: Output Formateado con Rich 🎯 PRIORIDAD MEDIA

**Objetivo:** Salida visual profesional en consola

#### Ticket 4.1: Implementar formatter con Rich
- **Archivo:** `src/quality_agents/codeguard/formatter.py` (nuevo)
- **Descripción:** Crear módulo para formatear output con Rich
- **Criterios de aceptación:**
  - [ ] Función `format_results(results: List[CheckResult], elapsed: float) -> None`
  - [ ] Usar Rich Console, Panel, Table
  - [ ] Header con logo/nombre
  - [ ] Resultados agrupados por severidad (ERROR, WARN, INFO)
  - [ ] Colores: rojo=ERROR, amarillo=WARN, azul=INFO, verde=PASS
  - [ ] Summary con contadores
  - [ ] Tiempo de ejecución
  - [ ] Sugerencias al final
  - [ ] Test visual manual
- **Estimación:** 3-4 horas

#### Ticket 4.2: Agregar modo JSON
- **Archivo:** `src/quality_agents/codeguard/formatter.py`
- **Descripción:** Soportar output en formato JSON
- **Criterios de aceptación:**
  - [ ] Función `format_json(results: List[CheckResult]) -> str`
  - [ ] Serializar CheckResult a dict
  - [ ] JSON pretty-printed
  - [ ] Argumento CLI `--format json`
  - [ ] Test de serialización
- **Estimación:** 1-2 horas

#### Ticket 4.3: Integrar formatter en agent.py
- **Archivo:** `src/quality_agents/codeguard/agent.py`
- **Descripción:** Usar formatter según opción CLI
- **Criterios de aceptación:**
  - [ ] Leer formato de CLI args (`--format`)
  - [ ] Si `text` → usar Rich formatter
  - [ ] Si `json` → usar JSON formatter
  - [ ] Default = `text`
  - [ ] Test con ambos formatos
- **Estimación:** 1 hora

**Total Fase 4:** 5-7 horas

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

| Fase | Descripción | Horas | Prioridad | Estado |
|------|-------------|-------|-----------|--------|
| 1 | Configuración moderna (pyproject.toml) | 4-6 | CRÍTICA | ✅ COMPLETADA |
| **1.5** | **Fundamentos de arquitectura modular** | **5.5-7.5** | **CRÍTICA** | ⏳ PENDIENTE |
| 2 | Migración a arquitectura modular | 13-16 | ALTA | ⏳ PENDIENTE |
| **2.5** | **Integración con orquestador** | **5-7** | **ALTA** | ⏳ PENDIENTE |
| 3 | IA opcional con Claude | 7-8 | MEDIA | ⏳ PENDIENTE |
| 4 | Output formateado con Rich | 5-7 | MEDIA | ⏳ PENDIENTE |
| 5 | Soporte pre-commit framework | 2 | MEDIA | ⏳ PENDIENTE |
| 6 | Tests y documentación | 7-9 | MEDIA | ⏳ PENDIENTE |
| **TOTAL** | **MVP Funcional con Arquitectura Modular** | **49-67.5 horas** | - | **30% completo** |

**Incremento vs plan original:** +11-13.5 horas por arquitectura modular
**Justificación:** Inversión en calidad arquitectónica, extensibilidad y mantenibilidad

**Estimación conservadora:** 7-9 días de trabajo (8h/día)

---

## Orden Recomendado de Ejecución

Para maximizar valor incremental con arquitectura modular:

### Sprint 1 (Prioridad CRÍTICA-ALTA): Fases 1.5, 2, 2.5
- **Objetivo:** Sistema modular funcional con checks reales
- **Resultado:** CodeGuard con arquitectura modular + 6 checks + orquestación
- **Horas:** ~24-30.5 horas
- **Valor:** Base arquitectónica sólida para futuro

### Sprint 2 (Prioridad MEDIA): Fases 3, 4
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
- [ ] Se instala con `pip install quality-agents`
- [ ] Comando `codeguard .` funciona
- [ ] Lee configuración desde `pyproject.toml` o `.yml`
- [ ] Ejecuta los 6 checks de calidad correctamente **como clases modulares**
- [ ] **Orquestador selecciona checks contextualmente** (nuevo criterio)
- [ ] Termina en < 5 segundos en pre-commit (sin errores ~2s)
- [ ] Termina en ~4s con errores + IA habilitada
- [ ] IA opcional funciona cuando se habilita
- [ ] Output en consola es legible y profesional
- [ ] Soporta pre-commit framework

**Arquitectura:**
- [ ] **Clase base `Verifiable` funcional** (nuevo criterio)
- [ ] **CheckOrchestrator con auto-discovery** (nuevo criterio)
- [ ] **6 checks como clases independientes** (nuevo criterio)
- [ ] Fácil agregar nuevos checks (crear clase + exportar)

**Calidad:**
- [ ] Tiene al menos 80% de cobertura de tests
- [ ] Tests de orquestación pasando
- [ ] README documenta uso básico y arquitectura
- [ ] Ejemplo funcional en `examples/`

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
- [ ] Implementación de arquitectura modular (Fase 1.5 - próximo)

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

**Próximo:** Fase 1.5 - Crear clase base Verifiable + CheckOrchestrator

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

**Última actualización:** 2026-02-02 (Rediseño Arquitectónico)
**Próximo milestone:** Fase 1.5 - Fundamentos de Arquitectura Modular
