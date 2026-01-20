# Plan de Implementación - CodeGuard

**Fecha de creación:** 2026-01-20
**Estado:** En Progreso
**Versión objetivo:** 0.1.0 (MVP Funcional)

---

## Contexto

Este documento define el plan de implementación/refactorización de CodeGuard alineado con:
- Decisiones arquitectónicas (Enero 2026) en `docs/agentes/ajuste_documentacion.md`
- Especificación v1.1 en `docs/agentes/especificacion_agentes_calidad.md`
- Plan general en `plan/plan_proyecto.md`

## Objetivos del MVP

CodeGuard debe ser un agente funcional que:
1. ✅ Se ejecuta en < 5 segundos (< 2s sin errores)
2. ✅ Lee configuración desde `pyproject.toml` (con fallback a `.yml`)
3. ✅ Ejecuta 6 checks de calidad (flake8, pylint, bandit, radon, mypy, imports)
4. ✅ Usa IA opcional para explicar errores (opt-in)
5. ✅ Genera output formateado con Rich
6. ✅ Es instalable como paquete y usable desde CLI
7. ✅ Soporta pre-commit framework

---

## Estado Actual

### ✅ Implementado (30%)

- [x] Estructura básica de clases (`CodeGuard`, `CheckResult`, `Severity`)
- [x] CLI con click (`agent.py:main()`)
- [x] Método `collect_files()` funcional
- [x] Dataclass `CodeGuardConfig` para configuración
- [x] Carga desde YAML (método `from_yaml()`)
- [x] Entry point en `pyproject.toml` (`codeguard` command)
- [x] Tests unitarios básicos

### ❌ Faltante (70%)

- [ ] Carga de configuración desde `pyproject.toml` (decisión #3)
- [ ] Implementación real de checks (todos están con `TODO`)
- [ ] Integración IA opcional con Claude API (decisión #4 y #5)
- [ ] Output formateado con Rich
- [ ] Configuración de IA en `CodeGuardConfig`
- [ ] `.pre-commit-hooks.yaml` para framework
- [ ] Tests de integración
- [ ] Documentación de uso

---

## Fases de Implementación

### Fase 1: Configuración Moderna (Decisión #3) 🎯 PRIORIDAD ALTA

**Objetivo:** Soportar configuración desde `pyproject.toml` con fallback a `.yml`

#### Ticket 1.1: Agregar soporte para pyproject.toml ✅ COMPLETADO
- **Archivo:** `src/quality_agents/codeguard/config.py`
- **Descripción:** Implementar método `from_pyproject_toml()`
- **Dependencias:** `tomli` (Python < 3.11) o `tomllib` (Python 3.11+)
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

#### Ticket 1.2: Implementar búsqueda en orden de prioridad
- **Archivo:** `src/quality_agents/codeguard/config.py`
- **Descripción:** Función `load_config()` que busca en orden: pyproject.toml → .codeguard.yml → defaults
- **Criterios de aceptación:**
  - [ ] Buscar primero en `pyproject.toml` (raíz proyecto)
  - [ ] Si no existe o no tiene `[tool.codeguard]`, buscar `.codeguard.yml`
  - [ ] Si ninguno existe, usar `CodeGuardConfig()` defaults
  - [ ] Logging de qué archivo se usó
  - [ ] Test con cada escenario
- **Estimación:** 1-2 horas

#### Ticket 1.3: Agregar configuración de IA
- **Archivo:** `src/quality_agents/codeguard/config.py`
- **Descripción:** Agregar dataclass `AIConfig` y campo en `CodeGuardConfig`
- **Criterios de aceptación:**
  - [ ] Crear `@dataclass AIConfig` con: `enabled`, `explain_errors`, `suggest_fixes`, `max_tokens`
  - [ ] Agregar campo `ai: AIConfig` en `CodeGuardConfig`
  - [ ] Defaults: `enabled=False` (opt-in)
  - [ ] Parsear desde pyproject.toml subsección `[tool.codeguard.ai]`
  - [ ] Tests
- **Estimación:** 1 hora

**Total Fase 1:** 4-6 horas

---

### Fase 2: Implementación de Checks Reales 🎯 PRIORIDAD ALTA

**Objetivo:** Implementar los 6 checks de calidad con herramientas reales

#### Ticket 2.1: Check PEP8 con flake8
- **Archivo:** `src/quality_agents/codeguard/checks.py`
- **Descripción:** Implementar `check_pep8(file_path) -> List[CheckResult]`
- **Criterios de aceptación:**
  - [ ] Ejecutar flake8 via subprocess
  - [ ] Parsear output para extraer violaciones
  - [ ] Crear `CheckResult` por cada violación con file_path y line_number
  - [ ] Severity = WARNING
  - [ ] Sugerencia: "Run 'black .' to auto-format"
  - [ ] Test con archivo que tiene violaciones
  - [ ] Test con archivo limpio
- **Estimación:** 2-3 horas

#### Ticket 2.2: Check Pylint score
- **Archivo:** `src/quality_agents/codeguard/checks.py`
- **Descripción:** Implementar `check_pylint_score(file_path, min_score) -> List[CheckResult]`
- **Criterios de aceptación:**
  - [ ] Ejecutar pylint via subprocess
  - [ ] Parsear output para extraer score (línea "Your code has been rated...")
  - [ ] Comparar con `min_score` del config
  - [ ] Severity = WARNING si score < min_score, INFO si >= min_score
  - [ ] Incluir score en message
  - [ ] Test con score alto y bajo
- **Estimación:** 2 horas

#### Ticket 2.3: Check Security con bandit
- **Archivo:** `src/quality_agents/codeguard/checks.py`
- **Descripción:** Implementar `check_security_issues(file_path) -> List[CheckResult]`
- **Criterios de aceptación:**
  - [ ] Ejecutar bandit con formato JSON
  - [ ] Parsear resultados
  - [ ] Filtrar issues HIGH severity → ERROR
  - [ ] Filtrar issues MEDIUM severity → WARNING
  - [ ] Incluir line_number y descripción de issue
  - [ ] Sugerencias específicas por tipo de issue (B201, B301, etc.)
  - [ ] Tests con código inseguro (hardcoded secret, eval, etc.)
- **Estimación:** 3 horas

#### Ticket 2.4: Check Complejidad Ciclomática con radon
- **Archivo:** `src/quality_agents/codeguard/checks.py`
- **Descripción:** Implementar `check_cyclomatic_complexity(file_path, max_cc) -> List[CheckResult]`
- **Criterios de aceptación:**
  - [ ] Ejecutar radon cc
  - [ ] Parsear output para extraer funciones con CC > max_cc
  - [ ] Severity = INFO (solo informativo, no bloquea)
  - [ ] Incluir nombre de función y CC en message
  - [ ] Sugerencia: "Consider refactoring into smaller functions"
  - [ ] Test con función compleja
- **Estimación:** 2 horas

#### Ticket 2.5: Check Type Errors con mypy
- **Archivo:** `src/quality_agents/codeguard/checks.py`
- **Descripción:** Implementar `check_type_errors(file_path) -> List[CheckResult]`
- **Criterios de aceptación:**
  - [ ] Verificar si archivo tiene type hints primero
  - [ ] Si no tiene hints, retornar lista vacía
  - [ ] Si tiene hints, ejecutar mypy
  - [ ] Parsear errores de tipo
  - [ ] Severity = WARNING
  - [ ] Incluir line_number
  - [ ] Test con archivo con/sin hints
- **Estimación:** 2-3 horas

#### Ticket 2.6: Check Unused Imports
- **Archivo:** `src/quality_agents/codeguard/checks.py`
- **Descripción:** Implementar `check_unused_imports(file_path) -> List[CheckResult]`
- **Criterios de aceptación:**
  - [ ] Usar pylint o autoflake para detectar imports sin uso
  - [ ] Parsear output
  - [ ] Severity = WARNING
  - [ ] Sugerencia: "Run 'autoflake --remove-unused-variables .' to auto-fix"
  - [ ] Test con imports sin uso
- **Estimación:** 2 horas

**Total Fase 2:** 13-16 horas

---

### Fase 3: Integración de Checks en Agent 🎯 PRIORIDAD ALTA

**Objetivo:** Ejecutar todos los checks desde `CodeGuard.run()`

#### Ticket 3.1: Integrar checks en método run()
- **Archivo:** `src/quality_agents/codeguard/agent.py`
- **Descripción:** Llamar todos los checks desde `run()` y agregar resultados
- **Criterios de aceptación:**
  - [ ] Importar funciones de checks desde `checks.py`
  - [ ] Llamar cada check si está habilitado en config
  - [ ] Agregar todos los `CheckResult` a `self.results`
  - [ ] Filtrar archivos por `exclude_patterns`
  - [ ] Medir tiempo de ejecución
  - [ ] Asegurar que termina en < 5s
  - [ ] Test de integración con múltiples archivos
- **Estimación:** 2 horas

#### Ticket 3.2: Gestión de errores y timeouts
- **Archivo:** `src/quality_agents/codeguard/agent.py`
- **Descripción:** Manejar errores de herramientas y timeouts
- **Criterios de aceptación:**
  - [ ] Try/except en cada llamada a check
  - [ ] Si una herramienta falla, agregar CheckResult con ERROR
  - [ ] No detener ejecución, continuar con otros checks
  - [ ] Timeout de 5s total
  - [ ] Log de errores
  - [ ] Test con herramienta que falla
- **Estimación:** 2 horas

**Total Fase 3:** 4 horas

---

### Fase 4: IA Opcional con Claude (Decisión #4 y #5) 🎯 PRIORIDAD MEDIA

**Objetivo:** Agregar explicaciones inteligentes de errores usando Claude API

#### Ticket 4.1: Crear módulo de integración IA
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

#### Ticket 4.2: Integrar IA en flujo de CodeGuard
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

#### Ticket 4.3: Formatear output de IA
- **Archivo:** `src/quality_agents/codeguard/ai_suggestions.py`
- **Descripción:** Formatear respuesta de Claude en formato legible
- **Criterios de aceptación:**
  - [ ] Parsear markdown de respuesta
  - [ ] Separar explicación de sugerencias
  - [ ] Formatear para consola con Rich
  - [ ] Limitar a `max_tokens` de config
  - [ ] Test con respuesta de ejemplo
- **Estimación:** 2 horas

**Total Fase 4:** 7-8 horas

---

### Fase 5: Output Formateado con Rich 🎯 PRIORIDAD MEDIA

**Objetivo:** Salida visual profesional en consola

#### Ticket 5.1: Implementar formatter con Rich
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

#### Ticket 5.2: Agregar modo JSON
- **Archivo:** `src/quality_agents/codeguard/formatter.py`
- **Descripción:** Soportar output en formato JSON
- **Criterios de aceptación:**
  - [ ] Función `format_json(results: List[CheckResult]) -> str`
  - [ ] Serializar CheckResult a dict
  - [ ] JSON pretty-printed
  - [ ] Argumento CLI `--format json`
  - [ ] Test de serialización
- **Estimación:** 1-2 horas

#### Ticket 5.3: Integrar formatter en agent.py
- **Archivo:** `src/quality_agents/codeguard/agent.py`
- **Descripción:** Usar formatter según opción CLI
- **Criterios de aceptación:**
  - [ ] Leer formato de CLI args (`--format`)
  - [ ] Si `text` → usar Rich formatter
  - [ ] Si `json` → usar JSON formatter
  - [ ] Default = `text`
  - [ ] Test con ambos formatos
- **Estimación:** 1 hora

**Total Fase 5:** 5-7 horas

---

### Fase 6: Soporte para pre-commit Framework 🎯 PRIORIDAD MEDIA

**Objetivo:** Habilitar uso con pre-commit framework (Decisión #2)

#### Ticket 6.1: Crear .pre-commit-hooks.yaml
- **Archivo:** `.pre-commit-hooks.yaml` (raíz del repositorio)
- **Descripción:** Definir hook para pre-commit framework
- **Criterios de aceptación:**
  - [ ] ID: `codeguard`
  - [ ] Name: "CodeGuard Quality Check"
  - [ ] Entry: `codeguard`
  - [ ] Language: `python`
  - [ ] Pass filenames: `false` (analiza todo el proyecto)
  - [ ] Files: `\.py$`
  - [ ] Always run: `false`
  - [ ] Test integrando en proyecto externo
- **Estimación:** 1 hora

#### Ticket 6.2: Documentar uso con pre-commit
- **Archivo:** `README.md` o `docs/guias/codeguard.md`
- **Descripción:** Agregar sección de integración con pre-commit
- **Criterios de aceptación:**
  - [ ] Ejemplo de `.pre-commit-config.yaml`
  - [ ] Comandos de instalación
  - [ ] Cómo ejecutar manualmente
  - [ ] Troubleshooting común
- **Estimación:** 1 hora

**Total Fase 6:** 2 horas

---

### Fase 7: Tests y Documentación 🎯 PRIORIDAD MEDIA

**Objetivo:** Asegurar calidad y usabilidad

#### Ticket 7.1: Tests de integración end-to-end
- **Archivo:** `tests/integration/test_codeguard_integration.py`
- **Descripción:** Test completo de flujo
- **Criterios de aceptación:**
  - [ ] Crear proyecto temporal con código de ejemplo
  - [ ] Ejecutar codeguard sobre el proyecto
  - [ ] Verificar que detecta errores esperados
  - [ ] Verificar tiempo < 5s
  - [ ] Test con IA habilitada/deshabilitada
  - [ ] Test con configuración desde pyproject.toml
  - [ ] Test con configuración desde .yml
  - [ ] Test sin configuración (defaults)
- **Estimación:** 3-4 horas

#### Ticket 7.2: Actualizar README.md
- **Archivo:** `README.md`
- **Descripción:** Documentar instalación y uso básico de CodeGuard
- **Criterios de aceptación:**
  - [ ] Sección de instalación
  - [ ] Ejemplos de uso (4 modelos de integración)
  - [ ] Configuración básica
  - [ ] Configuración de IA
  - [ ] FAQ
  - [ ] Screenshots o ejemplos de output
- **Estimación:** 2-3 horas

#### Ticket 7.3: Crear ejemplo funcional
- **Archivo:** `examples/sample_project/` (actualizar)
- **Descripción:** Proyecto de ejemplo con CodeGuard configurado
- **Criterios de aceptación:**
  - [ ] Código Python con algunos problemas de calidad
  - [ ] `pyproject.toml` con configuración de CodeGuard
  - [ ] `.pre-commit-config.yaml` configurado
  - [ ] README explicando el ejemplo
  - [ ] Script para probarlo
- **Estimación:** 2 horas

**Total Fase 7:** 7-9 horas

---

## Resumen de Estimaciones

| Fase | Descripción | Horas | Prioridad |
|------|-------------|-------|-----------|
| 1 | Configuración moderna (pyproject.toml) | 4-6 | ALTA |
| 2 | Implementación de checks reales | 13-16 | ALTA |
| 3 | Integración en agent | 4 | ALTA |
| 4 | IA opcional con Claude | 7-8 | MEDIA |
| 5 | Output formateado con Rich | 5-7 | MEDIA |
| 6 | Soporte pre-commit framework | 2 | MEDIA |
| 7 | Tests y documentación | 7-9 | MEDIA |
| **TOTAL** | **MVP Funcional** | **42-54 horas** | - |

**Estimación conservadora:** 6-7 días de trabajo (8h/día)

---

## Orden Recomendado de Ejecución

Para maximizar valor incremental:

1. **Sprint 1 (Prioridad ALTA):** Fases 1, 2, 3
   - Resultado: CodeGuard funcional con checks reales
   - ~21-26 horas

2. **Sprint 2 (Prioridad MEDIA):** Fases 4, 5
   - Resultado: IA opcional + output profesional
   - ~12-15 horas

3. **Sprint 3 (Finalización):** Fases 6, 7
   - Resultado: Integración completa + documentación
   - ~9-11 horas

---

## Criterios de Éxito del MVP

CodeGuard estará listo cuando:

- [ ] Se instala con `pip install quality-agents`
- [ ] Comando `codeguard .` funciona
- [ ] Lee configuración desde `pyproject.toml` o `.yml`
- [ ] Ejecuta los 6 checks de calidad correctamente
- [ ] Termina en < 5 segundos (sin errores), ~4s (con errores + IA)
- [ ] IA opcional funciona cuando se habilita
- [ ] Output en consola es legible y profesional
- [ ] Soporta pre-commit framework
- [ ] Tiene al menos 80% de cobertura de tests
- [ ] README documenta uso básico
- [ ] Ejemplo funcional en `examples/`

---

## Registro de Progreso

### 2026-01-20: Plan creado
- [x] Análisis de estado actual
- [x] Definición de fases y tickets
- [x] Estimaciones de esfuerzo

### 2026-01-20: Ticket 1.1 completado ✅
- [x] Implementado método `from_pyproject_toml()`
- [x] Creada dataclass `AIConfig`
- [x] Actualizado `from_yaml()` para soportar configuración de IA
- [x] Actualizado `to_yaml()` para incluir configuración de IA
- [x] Agregada dependencia `tomli` condicional en pyproject.toml
- [x] Creado archivo de tests `test_codeguard_config.py` con 11 tests
- [x] Todos los tests pasando ✅

**Cambios realizados:**
- `src/quality_agents/codeguard/config.py`: +80 líneas (AIConfig, from_pyproject_toml)
- `tests/unit/test_codeguard_config.py`: Nuevo archivo, 180 líneas, 11 tests
- `pyproject.toml`: +1 dependencia (tomli)

**Próximo:** Ticket 1.2 - Implementar búsqueda en orden de prioridad

---

## Notas Técnicas

### Dependencias a Agregar

En `pyproject.toml`:

```toml
dependencies = [
    # ... existentes
    "anthropic>=0.8.0",  # IA (ya está)
    "rich>=13.7.0",      # Output (ya está)
    "tomli>=2.0.0; python_version < '3.11'",  # NUEVO: leer pyproject.toml
]
```

### Configuración de Herramientas Externas

Flake8, Pylint, Bandit ya están como dependencias. Verificar que estén en `pyproject.toml`.

---

**Última actualización:** 2026-01-20
