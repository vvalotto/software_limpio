# SESION.md

> **INSTRUCCIÓN**: Lee este documento al inicio de cada sesión para obtener contexto completo del proyecto y continuar el trabajo donde quedó.

---

## Contexto del Proyecto

**Software Limpio** es un framework educativo y práctico que implementa control de calidad automatizado para proyectos Python, inspirado en la trilogía de Robert C. Martin (Clean Code, Clean Architecture) con el objetivo de agregar "Clean Design".

### Visión
Transformar a los desarrolladores de "escritores de código" a "evaluadores de calidad" mediante agentes de IA que detectan, explican y sugieren mejoras en tiempo real.

### Los Tres Agentes

| Agente | Momento | Duración | Acción |
|--------|---------|----------|--------|
| **CodeGuard** | Pre-commit | < 5 seg | Advierte (no bloquea) |
| **DesignReviewer** | PR/Review | 2-5 min | Bloquea si crítico |
| **ArchitectAnalyst** | Fin sprint | 10-30 min | Analiza tendencias |

### Principios Fundamentales (6)
1. Modularidad (Parnas 1972)
2. Ocultamiento de información (Parnas 1972)
3. Cohesión (Constantine 1968)
4. Acoplamiento (Constantine 1968)
5. Separación de concerns (Dijkstra 1974)
6. Abstracción (Liskov 1974)

---

## Estado Actual

### Última Sesión: 2026-01-20

**Branch activo**: `refactoring-fase-1-codeguard`

**Último commit**: `13a9967` - Actualizar CLAUDE.md con progreso de CodeGuard Fase 1

### Completado

- [x] Documentación base del proyecto (specs de agentes, catálogo de métricas)
- [x] Reorganización de estructura del proyecto
- [x] Creación de `src/quality_agents/` con estructura de los 3 agentes
- [x] Esqueletos de código para CodeGuard, DesignReviewer, ArchitectAnalyst
- [x] Módulo `shared/` para código común
- [x] Tests unitarios básicos (estructura)
- [x] Configuraciones YAML para cada agente
- [x] `pyproject.toml` para instalación del paquete
- [x] Proyecto de ejemplo (`examples/sample_project/`)
- [x] Plan del proyecto (`plan/plan_proyecto.md`)
- [x] `.gitignore` completo
- [x] `CLAUDE.md` actualizado con visión del proyecto y principios fundamentales
- [x] `SESION.md` creado (documento de contexto entre sesiones)
- [x] Comandos personalizados de Claude Code (`/sesion`, `/guardar-sesion`)
- [x] Hook SessionEnd para recordar guardar sesión
- [x] **Fase 0 completa**: Documentación teórica completa
  - [x] Estructura `docs/teoria/` con 4 secciones completas
  - [x] `docs/teoria/GUIA_REDACCION.md` - Estilo de escritura
  - [x] **Fundamentos**: 6 principios fundamentales documentados en `docs/teoria/fundamentos/`
  - [x] **Marco Filosófico**: Cuatro virtudes, antifragilidad, sistemas complejos
  - [x] **Nuevo Paradigma**: Rol profesional (4 competencias) y triángulo de competencias
  - [x] **Trilogía Limpia**: Código limpio, Diseño limpio, Arquitectura limpia
- [x] **Decisiones arquitectónicas** (Enero 2026)
  - [x] 5 decisiones clave documentadas en `docs/agentes/ajuste_documentacion.md`
  - [x] Modelo de distribución: Híbrido (Package + Hooks)
  - [x] Modelo de integración: Todos (CLI, pre-commit, hooks, CI/CD)
  - [x] Configuración: pyproject.toml (PEP 518) con fallback YAML
  - [x] Nomenclatura: Todos son agentes (CodeGuard con IA ligera)
  - [x] IA en CodeGuard: Opcional (opt-in)
- [x] **Fase 1 - CodeGuard: Configuración Moderna** ✅ COMPLETA
  - [x] Función `main()` con click
  - [x] Opciones: PATH, --config, --format
  - [x] Método `collect_files()` para recolectar archivos .py
  - [x] **Ticket 1.1**: Soporte pyproject.toml con `[tool.codeguard]`
  - [x] **Ticket 1.2**: Función `load_config()` con búsqueda automática
  - [x] **Ticket 1.3**: Configuración de IA con `AIConfig` (opt-in)
  - [x] 19 tests unitarios pasando (100% cobertura de configuración)
  - [x] `PLAN_IMPLEMENTACION.md` con roadmap completo (7 fases, 27 tickets)
- [x] Guías de usuario (`docs/guias/codeguard.md`)
- [x] `CLAUDE.md` actualizado con estado Fase 1

### En Progreso

- [ ] **Fase 2: CodeGuard - Implementación de Checks Reales** (Próximo paso)
  - [ ] Ticket 2.1: Check PEP8 con flake8
  - [ ] Ticket 2.2: Check Pylint score
  - [ ] Ticket 2.3: Check Security con bandit
  - [ ] Ticket 2.4: Check Complejidad con radon
  - [ ] Ticket 2.5: Check Type Errors con mypy
  - [ ] Ticket 2.6: Check Unused Imports

### Pendiente (Próximas Tareas)

**Prioridad Alta (P1)**:
1. **Completar Fase 2 de CodeGuard**: Implementar los 6 checks reales (~13-16 horas)
2. **Completar Fase 3 de CodeGuard**: Integrar checks en `CodeGuard.run()` (~4 horas)
3. Implementar `designreviewer/analyzers.py` con métricas reales (LCOM, CBO, MI)
4. Integrar Claude API en `designreviewer/ai_integration.py`

**Prioridad Media (P2)**:
5. **Completar Fases 4-5 de CodeGuard**: IA opcional + Rich output (~12-15 horas)
6. Implementar `architectanalyst/metrics.py` (métricas de Martin)
7. Implementar `architectanalyst/snapshots.py` (persistencia SQLite)
8. Crear reportes HTML con Jinja2
9. Dashboard con Plotly

**Prioridad Baja (P3)**:
10. **Completar Fases 6-7 de CodeGuard**: pre-commit + tests + docs (~9-11 horas)
11. GitHub Actions CI/CD
12. Documentación académica para publicación

---

## Estructura del Proyecto

```
software_limpio/
├── src/quality_agents/       # Código fuente (paquete instalable)
│   ├── codeguard/            # ← Fase 1 COMPLETA (config), Fase 2 en progreso (checks)
│   │   ├── config.py         # ✅ pyproject.toml + AIConfig + load_config()
│   │   ├── checks.py         # ← IMPLEMENTAR checks reales
│   │   └── PLAN_IMPLEMENTACION.md  # ✅ Roadmap completo
│   ├── designreviewer/       # ← IMPLEMENTAR ANÁLISIS + IA
│   ├── architectanalyst/     # ← IMPLEMENTAR MÉTRICAS
│   └── shared/               # Utilidades comunes
├── tests/                    # Tests (unit, integration, e2e)
│   └── unit/
│       └── test_codeguard_config.py  # ✅ 19 tests pasando
├── docs/                     # Documentación
│   ├── teoria/               # ✓ COMPLETA (4 secciones)
│   │   ├── fundamentos/      # ✓ 6 principios documentados
│   │   ├── marco_filosofico/ # ✓ Virtudes, antifragilidad, sistemas
│   │   ├── trilogia_limpia/  # ✓ Código, Diseño, Arquitectura
│   │   └── nuevo_paradigma/  # ✓ Rol profesional, triángulo
│   ├── metricas/             # ✓ Catálogo completo
│   ├── agentes/              # ✓ Especificaciones + decisiones
│   │   ├── especificacion_agentes_calidad.md  # v1.1
│   │   ├── guia_implementacion_agentes.md
│   │   └── ajuste_documentacion.md  # ✅ 5 decisiones arquitectónicas
│   └── guias/                # ✓ Guías de usuario
├── configs/                  # Configuraciones YAML ✓
├── examples/                 # Proyecto de ejemplo ✓
├── plan/                     # Plan del proyecto ✓
├── .claude/                  # Configuración Claude Code ✓
│   ├── commands/             # Comandos personalizados
│   └── settings.json         # Hooks (SessionStart, SessionEnd)
├── pyproject.toml            # Setup ✓ (con tomli condicional)
├── CLAUDE.md                 # Guía técnica ✓ (actualizado Fase 1)
└── SESION.md                 # Este archivo ✓
```

---

## Archivos Clave para Referencia

| Propósito | Archivo |
|-----------|---------|
| Especificación completa de agentes | `docs/agentes/especificacion_agentes_calidad.md` (v1.1) |
| Guía de implementación | `docs/agentes/guia_implementacion_agentes.md` |
| Decisiones arquitectónicas | `docs/agentes/ajuste_documentacion.md` (Enero 2026) |
| Plan de implementación CodeGuard | `src/quality_agents/codeguard/PLAN_IMPLEMENTACION.md` |
| Métricas clasificadas | `docs/metricas/Metricas_Clasificadas.md` |
| Plan detallado | `plan/plan_proyecto.md` |
| Configuración CodeGuard | `configs/codeguard.yml` (legacy fallback) |
| Guía de redacción teoría | `docs/teoria/GUIA_REDACCION.md` |
| 6 principios fundamentales | `docs/teoria/fundamentos/` |
| Marco filosófico | `docs/teoria/marco_filosofico/` |
| Trilogía limpia | `docs/teoria/trilogia_limpia/` |
| Nuevo paradigma | `docs/teoria/nuevo_paradigma/` |
| Guías de usuario | `docs/guias/` |

---

## Decisiones Técnicas Tomadas

1. **Python 3.11+** como versión mínima
2. **Estructura de paquete instalable** con `pip install -e ".[dev]"`
3. **Configuración:**
   - **CodeGuard**: `pyproject.toml` → `[tool.codeguard]` (PEP 518) con fallback a YAML
   - **Otros agentes**: YAML para configuración
4. **SQLite para histórico** de métricas de arquitectura
5. **Plotly para dashboards** (no Dash, no Streamlit)
6. **Claude API** para sugerencias inteligentes (modelo: claude-sonnet-4-20250514)
7. **Rich** para salida de consola con colores
8. **Jinja2** para reportes HTML
9. **Click** para CLI de los agentes
10. **tomllib/tomli** para parsear pyproject.toml (3.11+ / < 3.11)

---

## Comandos de Claude Code

```bash
# Cargar contexto de sesión (al inicio)
/sesion

# Guardar progreso de sesión (antes de salir)
/guardar-sesion
```

---

## Comandos Útiles

```bash
# Instalar en modo desarrollo
pip install -e ".[dev]"

# Ejecutar tests
pytest

# Ejecutar tests de configuración
pytest tests/unit/test_codeguard_config.py -v

# Probar CodeGuard
codeguard .                    # Directorio actual
codeguard src/                 # Directorio específico
codeguard --help               # Ver opciones

# Probar en otro proyecto
codeguard /ruta/a/otro/proyecto
```

---

## Notas para la Próxima Sesión

> Actualizar esta sección al final de cada sesión con contexto relevante.

### Progreso de esta sesión (2026-01-20):

**CodeGuard Fase 1 COMPLETADA** ✅ - 3 commits realizados:

1. **9cb11b0**: Ticket 1.1 - Soporte para pyproject.toml y configuración de IA
   - Implementado método `from_pyproject_toml()` en `CodeGuardConfig`
   - Creada dataclass `AIConfig` (opt-in por defecto)
   - Soporte para `[tool.codeguard]` y `[tool.codeguard.ai]`
   - Agregada dependencia condicional `tomli` para Python < 3.11
   - 11 tests unitarios creados (todos pasando)

2. **fcf52c3**: Ticket 1.2 - Implementar búsqueda en orden de prioridad
   - Función `load_config()` con búsqueda automática
   - Orden: config_path explícito → pyproject.toml → .codeguard.yml → defaults
   - Logging de archivo de configuración usado
   - 8 tests adicionales (19 tests totales pasando)
   - Actualizado `PLAN_IMPLEMENTACION.md` con progreso

3. **13a9967**: Actualizar CLAUDE.md con progreso de CodeGuard Fase 1
   - Nueva sección "CodeGuard Configuration" con ejemplos
   - Actualizado estado: 30% → 45%
   - Documentadas referencias a archivos nuevos
   - Agregada sección de dependencias (tomllib/tomli)

**Resultado:**
- ✅ Fase 1 completa: Sistema de configuración moderna
- ✅ 19 tests unitarios (100% pasando)
- ✅ Soporte completo para pyproject.toml
- ✅ Configuración de IA opcional (opt-in)
- ✅ Documentación actualizada

**Plan de implementación completo:**
- `src/quality_agents/codeguard/PLAN_IMPLEMENTACION.md`
- 7 fases, 27 tickets, 42-54 horas estimadas
- Fase 1: ✅ Completada (~3.5 horas)
- Fase 2: Pendiente (implementar 6 checks reales, ~13-16 horas)

### Para la próxima sesión:

- **Branch actual**: `refactoring-fase-1-codeguard`
- **Estado del proyecto**: 45% completo (Fase 1 de CodeGuard completa)
- **Próximo paso**: Fase 2 - Implementar checks reales
  - Ticket 2.1: Check PEP8 con flake8
  - Ticket 2.2: Check Pylint score
  - Ticket 2.3: Check Security con bandit
  - Ticket 2.4: Check Complejidad con radon
  - Ticket 2.5: Check Type Errors con mypy
  - Ticket 2.6: Check Unused Imports
- **Branches pendientes de PR**:
  - `fase-0-fundamentos` → puede mergearse a main (documentación teórica completa)
  - `refactoring-fase-1-codeguard` → en progreso (Fase 1 completa, continuar con Fase 2)
- **Tests**: 19 tests pasando en `test_codeguard_config.py`
- **Referencias importantes**:
  - `src/quality_agents/codeguard/PLAN_IMPLEMENTACION.md` - Roadmap detallado
  - `docs/agentes/ajuste_documentacion.md` - 5 decisiones arquitectónicas
  - `CLAUDE.md` - Actualizado con progreso Fase 1

---

*Última actualización: 2026-01-20*
