# Plan de Proyecto - Software Limpio

## Estado Actual del Proyecto

**Última actualización:** Enero 2026 (Revisión Arquitectónica)

---

## Decisiones Arquitectónicas (Enero 2026)

Se realizó una revisión arquitectónica completa documentada en `docs/agentes/ajuste_documentacion.md`. Las 5 decisiones clave tomadas:

### 1. Modelo de Distribución: Híbrido ✅
- Paquete instalable via `pip install quality-agents`
- También soporta pre-commit framework
- Justificación: Adopción profesional con máxima flexibilidad

### 2. Modelo de Integración: Todos los Modelos ✅
- Uso directo desde terminal
- Framework pre-commit (recomendado)
- Hook Git manual
- GitHub Actions / CI/CD
- Justificación: Soportar diversos workflows profesionales

### 3. Estructura de Configuración: pyproject.toml ✅
- Configuración en `[tool.codeguard]` siguiendo PEP 518
- Fallback a `.codeguard.yml` para compatibilidad
- Justificación: Estándar moderno de Python (black, ruff, pytest)

### 4. Nomenclatura: Todos son Agentes ✅
- Los tres componentes se llaman "agentes"
- CodeGuard tendrá IA ligera (opcional)
- DesignReviewer IA media (siempre)
- ArchitectAnalyst IA profunda (siempre)
- Justificación: Coherencia conceptual y técnica

### 5. Alcance de IA en CodeGuard: IA Opcional ✅
- IA solo si: errores detectados + usuario habilita
- Mantiene < 5s en commits limpios (~2s)
- Con errores + IA: ~4s
- Justificación: Balance entre valor agregado y restricción de tiempo

**Impacto en roadmap:** Las decisiones están reflejadas en la especificación actualizada (v1.1) y guía de implementación.

---

### Resumen de Completitud

| Componente | Documentación | Implementación | Estado Global |
|-----------|---------------|----------------|---------------|
| **Teoría - Fundamentos** | 100% | N/A | COMPLETO |
| **Teoría - Marco Filosófico** | 30% | N/A | EN PROGRESO |
| **Teoría - Trilogía Limpia** | 30% | N/A | EN PROGRESO |
| **Teoría - Nuevo Paradigma** | 30% | N/A | EN PROGRESO |
| **Métricas (Código)** | 100% | 0% | LISTO/NO CÓDIGO |
| **Métricas (Diseño)** | 100% | 0% | LISTO/NO CÓDIGO |
| **Métricas (Arquitectura)** | 100% | 0% | LISTO/NO CÓDIGO |
| **CodeGuard** | 100% | 70% | PARCIALMENTE FUNCIONAL |
| **DesignReviewer** | 100% | 5% | CRÍTICO |
| **ArchitectAnalyst** | 100% | 0% | NO INICIADO |
| **Ejemplos** | 5% | 0% | CRÍTICO |
| **Testing** | 0% | 0% | NO INICIADO |
| **CI/CD** | 50% | 0% | SOLO TEMPLATES |

### Fortalezas Identificadas

1. **Especificación Exhaustiva**: 1090 líneas de especificación clara y bien estructurada
2. **Catálogo Equilibrado**: 35 métricas seleccionadas de 155, bien curadas
3. **Roadmap Realista**: 4 fases con estimaciones de esfuerzo
4. **Triada de Agentes Coherente**: Pre-commit, On-demand, Sprint-end
5. **Base Teórica Documentada**: Referencias a Parnas, Martin, Constantine

### Debilidades Principales

1. **Brecha Teoría-Implementación**: 100% doc vs 10% código
2. **Falta de Ejemplos Reales**: No hay demostraciones en proyecto real
3. **IA sin Pruebas**: Integración con Claude definida pero no validada
4. **Testing Ausente**: Cero tests para validar agentes

---

## Plan de Desarrollo

### Fase 0: Fundamentos (Semana 1) ✓ COMPLETA

| Tarea | Prioridad | Estado | Descripción |
|-------|-----------|--------|-------------|
| Escribir principios fundamentales | P1 | ✓ | 6 principios en `docs/teoria/fundamentos/` |
| Crear `pyproject.toml` | P1 | ✓ | Proyecto instalable con dependencias |
| Tests básicos CodeGuard | P1 | ✓ | Tests unitarios existentes |
| Estructura docs/teoria/ | P1 | ✓ | 4 secciones: fundamentos, marco_filosofico, trilogia_limpia, nuevo_paradigma |
| Guía de redacción | P2 | ✓ | `docs/teoria/GUIA_REDACCION.md` |

**Entregables:**
- [x] `docs/teoria/fundamentos/` - Los 6 principios universales
- [x] `docs/teoria/GUIA_REDACCION.md` - Estilo de escritura
- [x] `pyproject.toml` con todas las dependencias
- [x] `tests/unit/test_codeguard.py`

---

### Fase 1: CodeGuard Funcional (Framework Usable)

**Objetivo:** CodeGuard como herramienta CLI instalable y usable en proyectos reales con arquitectura modular.

**Estado:** Actualizado con decisiones arquitectónicas de Enero 2026 + Febrero 2026 (Arquitectura Modular)

| Tarea | Prioridad | Estado | Descripción |
|-------|-----------|--------|-------------|
| CLI con click | P1 | ✅ | Función `main()` con argumentos: path, --config, --format |
| Carga de config desde pyproject.toml | P1 | ✅ | Leer `[tool.codeguard]` con fallback a .yml |
| **Arquitectura modular base** | **P0** | **⏳** | **Clase Verifiable + Orchestrator (Fase 1.5)** |
| Check: PEP8/flake8 (clase modular) | P1 | 🔄 | Migrar función a clase `PEP8Check` |
| Check: Pylint score (clase modular) | P1 | ⏳ | Implementar como `PylintCheck(Verifiable)` |
| Check: Seguridad/bandit (clase modular) | P1 | ⏳ | Implementar como `SecurityCheck(Verifiable)` |
| Check: Complejidad/radon (clase modular) | P1 | ⏳ | Implementar como `ComplexityCheck(Verifiable)` |
| Check: Types/mypy (clase modular) | P1 | ⏳ | Implementar como `TypesCheck(Verifiable)` |
| Check: Unused imports (clase modular) | P1 | ⏳ | Implementar como `ImportsCheck(Verifiable)` |
| Integración con orquestador | P1 | ⏳ | `CodeGuard.run()` usa `CheckOrchestrator` (Fase 2.5) |
| IA opcional para explicaciones | P1 | ⏳ | Claude API para explicar errores (opt-in) |
| Salida formateada con Rich | P1 | ⏳ | Output colorido en consola |
| Crear `.pre-commit-hooks.yaml` | P1 | ⏳ | Soporte para pre-commit framework |
| Documentación README | P1 | ⏳ | Instalación, uso, configuración, arquitectura |
| Tests de integración | P2 | ⏳ | Probar orquestación con `examples/sample_project/` |

**Uso esperado:**
```bash
pip install quality-agents              # Instalación
codeguard .                             # Analiza directorio actual
codeguard src/ --config my.yml          # Config personalizada
codeguard src/ --format json            # Salida JSON
codeguard . --analysis-type pre-commit  # Análisis rápido (<5s)
```

**Entregables:**
- [x] `src/quality_agents/codeguard/agent.py` con `main()` CLI
- [x] `src/quality_agents/codeguard/config.py` carga pyproject.toml + YAML
- [ ] **`src/quality_agents/shared/verifiable.py`** - Clase base (Fase 1.5)
- [ ] **`src/quality_agents/codeguard/orchestrator.py`** - Orquestador (Fase 1.5)
- [ ] **`src/quality_agents/codeguard/checks/`** - Checks modulares (Fase 2)
  - [ ] `pep8_check.py`, `pylint_check.py`, `security_check.py`
  - [ ] `complexity_check.py`, `types_check.py`, `imports_check.py`
- [ ] `README.md` actualizado con instalación y uso
- [ ] `.pre-commit-config.yaml`
- [ ] `tests/integration/test_codeguard_integration.py`
- [ ] `tests/integration/test_codeguard_orchestration.py`

**Estimación actualizada:** 49-67.5h (vs 42-54h original) = +11-13.5h por arquitectura modular

---

### Fase 2: DesignReviewer Funcional (Semanas 3-4)

| Tarea | Prioridad | Esfuerzo | Descripción |
|-------|-----------|----------|-------------|
| Análisis real de métricas | P1 | 8-10h | Implementar con radon, pydeps |
| Integración Claude API | P2 | 6-8h | Sugerencias inteligentes |
| Generador reportes HTML | P1 | 8-10h | Salida visual profesional |
| Tests e2e | P2 | 4-6h | Validar flujo completo |

**Entregables:**
- [ ] `src/quality_agents/designreviewer/` completo
- [ ] Templates HTML para reportes
- [ ] `/tests/e2e/test_designreviewer.py`

---

### Fase 3: ArchitectAnalyst MVP (Semanas 5-7)

| Tarea | Prioridad | Esfuerzo | Descripción |
|-------|-----------|----------|-------------|
| Métricas de Martin | P1 | 12-15h | Ca, Ce, I, A, D |
| Sistema snapshots/DB | P2 | 8-10h | SQLite para histórico |
| Dashboard Plotly | P2 | 10-12h | Visualización interactiva |
| Análisis tendencias | P2 | 6-8h | Detección de degradación |

**Entregables:**
- [ ] `src/quality_agents/architectanalyst/` completo
- [ ] Schema SQLite implementado
- [ ] Dashboard web funcional

---

### Fase 4: Integración y Ejemplos (Semanas 8-10)

| Tarea | Prioridad | Esfuerzo | Descripción |
|-------|-----------|----------|-------------|
| Proyecto ejemplo completo | P1 | 15-20h | En `/examples/sample_project/` |
| Casos antes/después | P2 | 8-12h | Demostrar mejoras con métricas |
| GitHub Actions CI/CD | P2 | 4-6h | Automatización completa |
| Documentación final | P2 | 6-8h | Pulir toda la documentación |

**Entregables:**
- [ ] `/examples/sample_project/` funcional
- [ ] Reportes de ejemplo generados
- [ ] `.github/workflows/quality-check.yml`

---

## Estructura Propuesta

### Estructura Actual
```
software_limpio/
├── teoria/
├── metricas/
├── agentes/
└── ejemplos/
```

### Estructura Nueva
```
software_limpio/
├── docs/                          # Documentación
│   ├── teoria/                    # Fundamentos teóricos
│   │   ├── principios_fundamentales.md
│   │   ├── historia.md
│   │   └── README.md
│   ├── metricas/                  # Catálogo de métricas
│   │   ├── catalogo_general.md
│   │   ├── codigo.md
│   │   ├── diseno.md
│   │   └── arquitectura.md
│   └── agentes/                   # Especificaciones
│       ├── especificacion_agentes_calidad.md
│       └── guia_implementacion_agentes.md
│
├── src/                           # Código fuente
│   └── quality_agents/            # Paquete Python
│       ├── __init__.py
│       ├── codeguard/
│       │   ├── __init__.py
│       │   ├── agent.py
│       │   ├── checks.py
│       │   └── config.py
│       ├── designreviewer/
│       │   ├── __init__.py
│       │   ├── agent.py
│       │   ├── analyzers.py
│       │   ├── reporters.py
│       │   └── ai_integration.py
│       ├── architectanalyst/
│       │   ├── __init__.py
│       │   ├── agent.py
│       │   ├── metrics.py
│       │   ├── snapshots.py
│       │   └── dashboard.py
│       └── shared/
│           ├── __init__.py
│           ├── config.py
│           └── reporting.py
│
├── tests/                         # Tests
│   ├── unit/
│   │   ├── test_codeguard.py
│   │   ├── test_designreviewer.py
│   │   └── test_architectanalyst.py
│   ├── integration/
│   ├── e2e/
│   └── conftest.py
│
├── examples/                      # Ejemplos
│   ├── sample_project/
│   │   ├── src/
│   │   └── tests/
│   └── reports/
│
├── configs/                       # Configuraciones
│   ├── codeguard.yml
│   ├── designreviewer.yml
│   └── architectanalyst.yml
│
├── plan/                          # Plan del proyecto
│   └── plan_proyecto.md
│
├── .github/                       # CI/CD
│   └── workflows/
│       └── quality-check.yml
│
├── pyproject.toml
├── CLAUDE.md
├── README.md
└── .gitignore
```

### Justificación de Cambios

| Cambio | Justificación |
|--------|---------------|
| `teoria/` → `docs/teoria/` | Agrupar documentación bajo `docs/` |
| `metricas/` → `docs/metricas/` | Consistencia de documentación |
| `agentes/` → `docs/agentes/` | Separar specs de implementación |
| Crear `src/quality_agents/` | Código como paquete instalable |
| Crear `tests/` | Testing estructurado (unit, integration, e2e) |
| Crear `configs/` | Configuraciones centralizadas |
| `ejemplos/` → `examples/` | Convención Python estándar |

---

## Dependencias del Proyecto

### Dependencias Core

```toml
[project]
dependencies = [
    # Control de Calidad
    "flake8>=6.0.0",
    "pylint>=3.0.0",
    "bandit>=1.7.5",
    "mypy>=1.7.0",
    "radon>=6.0.1",

    # Análisis de Dependencias
    "pydeps>=1.12.0",
    "pipdeptree>=2.13.0",

    # Integración IA
    "anthropic>=0.8.0",

    # Reportes
    "jinja2>=3.1.2",
    "plotly>=5.17.0",
    "rich>=13.7.0",

    # Utilidades
    "pyyaml>=6.0.1",
    "click>=8.1.7",
]
```

### Dependencias de Desarrollo

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "coverage>=7.3.0",
    "black>=23.0.0",
    "isort>=5.12.0",
]
```

---

## Prioridades Resumen

### Crítico (Bloquea Progreso)
1. ~~Escribir `/docs/teoria/principios_fundamentales.md`~~ ✓ COMPLETO
2. Completar `DesignReviewer` con análisis real
3. Crear `ArchitectAnalyst` desde cero

### Importante
4. Completar documentación teórica (marco filosófico, trilogía, nuevo paradigma)
5. Tests para validar funcionamiento
6. Proyecto ejemplo funcional

### Deseable
7. Dashboard web interactivo
8. CI/CD con GitHub Actions
9. Documentación académica

---

## Métricas de Éxito

| Fase | Criterio de Éxito | Estado |
|------|-------------------|--------|
| Fase 0 | 6 principios documentados, proyecto instalable | ✓ COMPLETO |
| Fase 1 | CodeGuard bloquea commits con errores críticos, 80% coverage | PENDIENTE |
| Fase 2 | DesignReviewer genera reportes HTML con sugerencias de IA | PENDIENTE |
| Fase 3 | ArchitectAnalyst muestra tendencias en dashboard | PENDIENTE |
| Fase 4 | Proyecto ejemplo demuestra mejora de métricas | PENDIENTE |

---

## Notas Adicionales

### Archivos de Referencia Existentes
- `Documentos de Trabajo local/`: 13 PDFs de investigación (no versionados)
- Repositorio externo: [ISSE_Termostato](https://github.com/vvalotto/ISSE_Termostato)

### Consideraciones Técnicas
- Python 3.13 requerido
- Integración con Claude API requiere key de Anthropic
- Dashboard usa Plotly (no requiere servidor separado)
