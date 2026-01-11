# Plan de Proyecto - Software Limpio

## Estado Actual del Proyecto

### Resumen de Completitud

| Componente | Documentación | Implementación | Estado Global |
|-----------|---------------|----------------|---------------|
| **Teoría** | 10% | 0% | BLOQUEANTE |
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

### Fase 0: Fundamentos (Semana 1)

| Tarea | Prioridad | Esfuerzo | Descripción |
|-------|-----------|----------|-------------|
| Escribir principios fundamentales | P1 | 4-6h | Crear `/docs/teoria/principios_fundamentales.md` con los 6 principios |
| Crear `pyproject.toml` | P1 | 2h | Configurar proyecto con dependencias |
| Tests básicos CodeGuard | P1 | 4-6h | Validar funcionamiento actual |

**Entregables:**
- [ ] `/docs/teoria/principios_fundamentales.md`
- [ ] `pyproject.toml` con todas las dependencias
- [ ] `/tests/unit/test_codeguard.py`

---

### Fase 1: CodeGuard Completo (Semana 2)

| Tarea | Prioridad | Esfuerzo | Descripción |
|-------|-----------|----------|-------------|
| Refinar codeguard.py | P2 | 4-6h | Mejorar logging, configuración YAML |
| Configurar pre-commit hook | P2 | 2h | Hook funcional en `.git/hooks/` |
| Tests de integración | P2 | 4h | Probar con proyecto real |

**Entregables:**
- [ ] `codeguard.py` refinado
- [ ] `.pre-commit-config.yaml`
- [ ] `/tests/integration/test_codeguard_integration.py`

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
1. Escribir `/docs/teoria/principios_fundamentales.md`
2. Completar `DesignReviewer` con análisis real
3. Crear `ArchitectAnalyst` desde cero

### Importante
4. Estructura de `src/` con paquete instalable
5. Tests para validar funcionamiento
6. Proyecto ejemplo funcional

### Deseable
7. Dashboard web interactivo
8. CI/CD con GitHub Actions
9. Documentación académica

---

## Métricas de Éxito

| Fase | Criterio de Éxito |
|------|-------------------|
| Fase 0 | 6 principios documentados, proyecto instalable con `pip install -e .` |
| Fase 1 | CodeGuard bloquea commits con errores críticos, 80% coverage en tests |
| Fase 2 | DesignReviewer genera reportes HTML con sugerencias de IA |
| Fase 3 | ArchitectAnalyst muestra tendencias en dashboard |
| Fase 4 | Proyecto ejemplo demuestra mejora de métricas post-refactoring |

---

## Notas Adicionales

### Archivos de Referencia Existentes
- `Documentos de Trabajo local/`: 13 PDFs de investigación (no versionados)
- Repositorio externo: [ISSE_Termostato](https://github.com/vvalotto/ISSE_Termostato)

### Consideraciones Técnicas
- Python 3.13 requerido
- Integración con Claude API requiere key de Anthropic
- Dashboard usa Plotly (no requiere servidor separado)
