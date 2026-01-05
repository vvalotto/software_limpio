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
1. Cohesión
2. Acoplamiento (minimizar)
3. Ocultamiento de información
4. Modularidad
5. Abstracción
6. Responsabilidad única

---

## Estado Actual

### Última Sesión: 2025-01-05

**Branch activo**: `configuracion-entorno`

**Último commit**: `c855d3a` - Reorganización completa de la estructura del proyecto

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
- [x] `CLAUDE.md` actualizado
- [x] `SESION.md` creado (documento de contexto entre sesiones)
- [x] Comandos personalizados de Claude Code (`/sesion`, `/guardar-sesion`)

### En Progreso

- [ ] Implementación real de CodeGuard (tiene esqueleto, falta lógica)
- [ ] Documentación de teoría (`docs/teoria/principios_fundamentales.md`)

### Pendiente (Próximas Tareas)

**Prioridad Alta (P1)**:
1. Escribir `docs/teoria/principios_fundamentales.md` - Los 6 principios con ejemplos
2. Implementar lógica real en `codeguard/checks.py` usando flake8, pylint, bandit, radon
3. Implementar `designreviewer/analyzers.py` con métricas reales (LCOM, CBO, MI)
4. Integrar Claude API en `designreviewer/ai_integration.py`

**Prioridad Media (P2)**:
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
│   ├── codeguard/            # ← IMPLEMENTAR LÓGICA
│   ├── designreviewer/       # ← IMPLEMENTAR ANÁLISIS + IA
│   ├── architectanalyst/     # ← IMPLEMENTAR MÉTRICAS
│   └── shared/               # Utilidades comunes
├── tests/                    # Tests (unit, integration, e2e)
├── docs/                     # Documentación
│   ├── teoria/               # ← ESCRIBIR PRINCIPIOS
│   ├── metricas/             # Catálogo completo ✓
│   └── agentes/              # Especificaciones ✓
├── configs/                  # Configuraciones YAML ✓
├── examples/                 # Proyecto de ejemplo ✓
├── plan/                     # Plan del proyecto ✓
├── .claude/                  # Configuración Claude Code ✓
│   ├── commands/             # Comandos personalizados
│   └── settings.json         # Hooks
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
| Ejemplo de código malo/bueno | `examples/sample_project/src/calculator.py` |

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

---

## Comandos de Claude Code

```bash
# Cargar contexto de sesión (al inicio)
/sesion

# Guardar progreso de sesión (antes de salir)
/guardar-sesion
```

**Nota**: Reiniciar Claude Code después de crear nuevos comandos para que los detecte.

---

## Comandos Útiles

```bash
# Instalar en modo desarrollo
pip install -e ".[dev]"

# Ejecutar tests
pytest

# Ver estructura
find . -type f -name "*.py" | grep -v venv | grep -v __pycache__ | head -30
```

---

## Notas para la Próxima Sesión

> Actualizar esta sección al final de cada sesión con contexto relevante.

- El proyecto está en branch `configuracion-entorno`, **pendiente hacer commit** de:
  - `SESION.md`
  - `.claude/` (comandos y settings)
- Después del commit, considerar hacer PR a `main`
- Los esqueletos de código están listos, falta implementar la lógica real
- Priorizar: (1) Teoría de principios, (2) CodeGuard funcional, (3) DesignReviewer con IA
- El usuario prefiere documentación en español
- Hay PDFs de investigación en `Documentos de Trabajo local/` (no versionados)
- **Para que funcionen los comandos `/sesion` y `/guardar-sesion`**: reiniciar Claude Code

---

*Última actualización: 2025-01-05*
