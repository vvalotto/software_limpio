# CLAUDE.md

Este archivo proporciona orientación a Claude Code (claude.ai/code) cuando trabaja con código en este repositorio.

## Descripción del Proyecto

**Software Limpio** es un framework en Python para métricas de calidad de software y agentes automatizados de control de calidad.

- **Lenguaje:** Python 3.11+
- **Entorno virtual:** `.venv`
- **Idioma de documentación:** Español

## Comandos de Desarrollo

```bash
# Instalación en modo desarrollo
pip install -e ".[dev]"

# Ejecutar tests
pytest

# Ejecutar tests con coverage
pytest --cov=src/quality_agents --cov-report=html

# Formatear código
black src/ tests/
isort src/ tests/

# Linting
ruff check src/ tests/
mypy src/
```

## Arquitectura

El proyecto implementa un **Sistema de Control de Calidad en Tres Niveles**:

```
Pre-commit (segundos)   →    Review (minutos)    →    Fin de sprint (horas)
         ↓                            ↓                         ↓
    CodeGuard               DesignReviewer           ArchitectAnalyst
   (solo ADVIERTE)          (BLOQUEA si crítico)     (ANALIZA tendencias)
```

### Los Tres Agentes

1. **CodeGuard** (`src/quality_agents/codeguard/`)
   - Pre-commit, < 5 segundos
   - Advertencias no bloqueantes: PEP8, Pylint, seguridad, tipos, complejidad

2. **DesignReviewer** (`src/quality_agents/designreviewer/`)
   - PR/Review, 2-5 minutos
   - Bloquea en críticos: code smells, cohesión (LCOM), acoplamiento (CBO)
   - Genera reportes HTML con sugerencias de IA

3. **ArchitectAnalyst** (`src/quality_agents/architectanalyst/`)
   - Fin de sprint, 10-30 minutos
   - Análisis: ciclos de dependencia, violaciones de capas, tendencias
   - Genera dashboard interactivo

## Estructura del Proyecto

```
software_limpio/
├── src/quality_agents/       # Código fuente
│   ├── codeguard/            # Agente pre-commit
│   ├── designreviewer/       # Agente de review
│   ├── architectanalyst/     # Agente de arquitectura
│   └── shared/               # Código compartido
├── tests/                    # Tests (unit, integration, e2e)
├── docs/                     # Documentación
│   ├── teoria/               # Fundamentos teóricos
│   ├── metricas/             # Catálogo de métricas
│   └── agentes/              # Especificaciones de agentes
├── configs/                  # Archivos de configuración YAML
├── examples/                 # Proyecto de ejemplo
└── plan/                     # Plan del proyecto
```

### Archivos de Documentación Clave

- `docs/agentes/especificacion_agentes_calidad.md` - Especificaciones detalladas
- `docs/agentes/guia_implementacion_agentes.md` - Guía de implementación
- `docs/metricas/Metricas_Clasificadas.md` - Clasificación de métricas
- `docs/metricas/catalogo_general.md` - Catálogo general

### Archivos de Configuración

- `configs/codeguard.yml` - Configuración de CodeGuard
- `configs/designreviewer.yml` - Configuración de DesignReviewer
- `configs/architectanalyst.yml` - Configuración de ArchitectAnalyst

## Principios de Diseño (Agnósticos al Paradigma)

1. **Cohesión** - Elementos relacionados juntos
2. **Acoplamiento** - Minimizar dependencias entre módulos
3. **Ocultamiento de Información** - Exponer solo lo necesario
4. **Modularidad** - Dividir en partes manejables
5. **Abstracción** - Separar el qué del cómo
6. **Responsabilidad Única** - Una sola razón para cambiar

## Umbrales de Métricas

| Nivel | Métrica | Umbral |
|-------|---------|--------|
| Código | Complejidad Ciclomática (CC) | ≤ 10 |
| Código | Líneas por función | ≤ 20 |
| Código | Profundidad de anidamiento | ≤ 4 |
| Diseño | CBO (Coupling Between Objects) | ≤ 5 |
| Diseño | LCOM (Lack of Cohesion) | ≤ 1 |
| Diseño | MI (Maintainability Index) | > 20 |
| Arquitectura | Distance from Main Sequence | ≈ 0 |
| Arquitectura | Violaciones de capa | = 0 |
| Arquitectura | Ciclos de dependencia | = 0 |

## Notas de Desarrollo

- Extiende la trilogía de Robert C. Martin con "Clean Design"
- Integración con Claude API para sugerencias inteligentes
- Repositorio de ejemplo: [ISSE_Termostato](https://github.com/vvalotto/ISSE_Termostato)
