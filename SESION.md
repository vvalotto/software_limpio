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

### Última Sesión: 2025-01-11

**Branch activo**: `fase-1-codeguard`

**Último commit**: `c40d3e5` - Implementar CLI básico de CodeGuard con click

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
- [x] `CLAUDE.md` actualizado con guía de redacción
- [x] `SESION.md` creado (documento de contexto entre sesiones)
- [x] Comandos personalizados de Claude Code (`/sesion`, `/guardar-sesion`)
- [x] Hook SessionEnd para recordar guardar sesión
- [x] **Fase 0 completa**: Documentación teórica de fundamentos
  - [x] Estructura `docs/teoria/` con 4 secciones (18 archivos)
  - [x] `docs/teoria/GUIA_REDACCION.md` - Estilo de escritura
  - [x] 6 principios fundamentales documentados en `docs/teoria/fundamentos/`
- [x] **Fase 1 iniciada**: CLI básico de CodeGuard
  - [x] Función `main()` con click
  - [x] Opciones: PATH, --config, --format
  - [x] Método `collect_files()` para recolectar archivos .py
  - [x] Probado en proyecto externo (ISSE_Termostato: 146 archivos)

### En Progreso

- [ ] **Fase 1: CodeGuard funcional** (CLI ya funciona, faltan checks)
  - [ ] Carga de configuración YAML
  - [ ] Check: flake8 (PEP8)
  - [ ] Check: pylint (análisis estático)
  - [ ] Check: bandit (seguridad)
  - [ ] Check: radon (complejidad)
  - [ ] Salida formateada con `rich`
  - [ ] Documentación en README

### Pendiente (Próximas Tareas)

**Prioridad Alta (P1)**:
1. Completar Fase 1: CodeGuard como framework usable
2. Implementar `designreviewer/analyzers.py` con métricas reales (LCOM, CBO, MI)
3. Integrar Claude API en `designreviewer/ai_integration.py`

**Prioridad Media (P2)**:
4. Completar docs/teoria/ (marco_filosofico, trilogia_limpia, nuevo_paradigma)
5. Implementar `architectanalyst/metrics.py` (métricas de Martin)
6. Implementar `architectanalyst/snapshots.py` (persistencia SQLite)
7. Crear reportes HTML con Jinja2
8. Dashboard con Plotly

**Prioridad Baja (P3)**:
9. GitHub Actions CI/CD
10. Documentación académica

---

## Estructura del Proyecto

```
software_limpio/
├── src/quality_agents/       # Código fuente (paquete instalable)
│   ├── codeguard/            # ← CLI funciona, faltan checks
│   ├── designreviewer/       # ← IMPLEMENTAR ANÁLISIS + IA
│   ├── architectanalyst/     # ← IMPLEMENTAR MÉTRICAS
│   └── shared/               # Utilidades comunes
├── tests/                    # Tests (unit, integration, e2e)
├── docs/                     # Documentación
│   ├── teoria/               # ✓ Estructura completa
│   │   ├── fundamentos/      # ✓ 6 principios documentados
│   │   ├── marco_filosofico/ # Placeholders
│   │   ├── trilogia_limpia/  # Placeholders
│   │   └── nuevo_paradigma/  # Placeholders
│   ├── metricas/             # Catálogo completo ✓
│   └── agentes/              # Especificaciones ✓
├── configs/                  # Configuraciones YAML ✓
├── examples/                 # Proyecto de ejemplo ✓
├── plan/                     # Plan del proyecto ✓
├── .claude/                  # Configuración Claude Code ✓
│   ├── commands/             # Comandos personalizados
│   └── settings.json         # Hooks (SessionStart, SessionEnd)
├── pyproject.toml            # Setup ✓
├── CLAUDE.md                 # Guía técnica ✓
└── SESION.md                 # Este archivo ✓
```

---

## Archivos Clave para Referencia

| Propósito | Archivo |
|-----------|---------|
| Especificación completa de agentes | `docs/agentes/especificacion_agentes_calidad.md` |
| Guía de implementación | `docs/agentes/guia_implementacion_agentes.md` |
| Métricas clasificadas | `docs/metricas/Metricas_Clasificadas.md` |
| Plan detallado | `plan/plan_proyecto.md` |
| Configuración CodeGuard | `configs/codeguard.yml` |
| Guía de redacción teoría | `docs/teoria/GUIA_REDACCION.md` |
| 6 principios fundamentales | `docs/teoria/fundamentos/` |

---

## Decisiones Técnicas Tomadas

1. **Python 3.11+** como versión mínima
2. **Estructura de paquete instalable** con `pip install -e ".[dev]"`
3. **YAML para configuración** de cada agente (no JSON, no TOML)
4. **SQLite para histórico** de métricas de arquitectura
5. **Plotly para dashboards** (no Dash, no Streamlit)
6. **Claude API** para sugerencias inteligentes (modelo: claude-sonnet-4)
7. **Rich** para salida de consola con colores
8. **Jinja2** para reportes HTML
9. **Click** para CLI de los agentes

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

- **Branch actual**: `fase-1-codeguard` - Continuar implementación de checks
- **Próximo paso**: Carga de configuración YAML, luego checks reales (flake8, pylint, bandit, radon)
- **Branches pendientes de PR**:
  - `fase-0-fundamentos` → listo para PR a main
  - `fase-1-codeguard` → en progreso
- **El CLI ya funciona**: `codeguard .` encuentra archivos Python, falta ejecutar los checks
- **Probado en ISSE_Termostato**: 146 archivos Python encontrados
- El usuario prefiere documentación en español
- Hay material de investigación en `Documentos de Trabajo local/` (no versionados)

---

*Última actualización: 2025-01-11*
