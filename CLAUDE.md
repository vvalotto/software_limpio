# CLAUDE.md

Este archivo provee orientación a Claude Code (claude.ai/code) cuando trabaja con código en este repositorio.

## Descripción del Proyecto

**Software Limpio** es un framework Python para control de calidad automatizado en tres niveles, inspirado en la trilogía de Robert C. Martin. Transforma a los desarrolladores de "escritores de código" a "evaluadores de calidad" mediante agentes de IA.

- **Lenguaje:** Python 3.11+
- **Nombre del paquete:** `quality-agents` (instalar con `pip install -e ".[dev]"`)
- **Idioma de documentación:** Español (rioplatense)
- **Entorno virtual:** `.venv`

## Comandos de Desarrollo

```bash
# Instalar en modo desarrollo
pip install -e ".[dev]"

# Ejecutar todos los tests (300 tests, ~15s)
pytest

# Ejecutar por categoría
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Ejecutar un test específico
pytest tests/unit/test_codeguard_config.py::TestLoadConfig::test_load_config_from_pyproject_toml

# Ejecutar con cobertura
pytest --cov=src/quality_agents --cov-report=html

# Formatear código (line-length=100)
black src/ tests/
isort src/ tests/

# Linting
ruff check src/ tests/
mypy src/
```

## Puntos de Entrada CLI

Después de `pip install -e ".[dev]"`:

```bash
codeguard .                              # Analiza el directorio actual (pre-commit, solo advierte)
codeguard src/ --format json             # Salida en JSON
codeguard --config configs/codeguard.yml # Configuración personalizada

designreviewer   # (implementación pendiente)
architectanalyst # (implementación pendiente)
```

## Arquitectura

Sistema de control de calidad en tres niveles:

```
Pre-commit (<5s)    →    PR Review (2-5min)    →    Fin de Sprint (10-30min)
      ↓                        ↓                           ↓
  CodeGuard              DesignReviewer             ArchitectAnalyst
 (solo advierte)       (bloquea si crítico)        (análisis de tendencias)
```

**CodeGuard es el único agente completo** (MVP). DesignReviewer y ArchitectAnalyst solo tienen estructura esqueleto.

### Estructura de Agentes

Cada agente vive en `src/quality_agents/<agente>/`:
- `agent.py` — Clase principal + CLI (punto de entrada `main()`)
- `orchestrator.py` — Selección y ejecución contextual de checks
- `checks/` (o `analyzers/`/`metrics/`) — Verificables modulares individuales
- `config.py` — Carga de configuración

Utilidades compartidas en `src/quality_agents/shared/`:
- `verifiable.py` — Clase base `Verifiable` + `ExecutionContext`
- `config.py` — Dataclass `QualityConfig`
- `reporting.py` — Generación de reportes

### Patrón Verifiable

Todos los checks heredan de `Verifiable` (`src/quality_agents/shared/verifiable.py`):

```python
class MyCheck(Verifiable):
    @property
    def name(self) -> str: return "MyCheck"
    @property
    def category(self) -> str: return "style"
    @property
    def estimated_duration(self) -> float: return 1.0
    @property
    def priority(self) -> int: return 3  # 1=mayor prioridad

    def should_run(self, context: ExecutionContext) -> bool: ...
    def execute(self, file_path: Path) -> List[CheckResult]: ...
```

Para agregar un nuevo check: crear el archivo en `checks/`, heredar de `Verifiable`, exportar en `__init__.py`. El auto-discovery se encarga del resto.

Cada check retorna `CheckResult(check_name, severity: Severity, message, file_path, line_number)` donde `Severity` es `INFO | WARNING | ERROR`.

### Checks de CodeGuard (todos implementados)

`PEP8Check` (flake8), `PylintCheck`, `SecurityCheck` (bandit), `ComplexityCheck` (radon), `TypeCheck` (mypy), `ImportCheck` (pylint).

### Carga de Configuración

**CodeGuard** usa `pyproject.toml` con fallback a YAML:
- Principal: sección `[tool.codeguard]` en `pyproject.toml`
- Fallback: `.codeguard.yml`
- Orden de búsqueda: ruta explícita → pyproject.toml → `.codeguard.yml` → defaults

**Otros agentes** usan YAML desde `configs/<agente>.yml` vía `QualityConfig.from_yaml()`.

Umbrales clave configurables (definidos en `QualityConfig.thresholds`):
- Complejidad Ciclomática ≤ 10, Líneas por función ≤ 20, Longitud de línea ≤ 100
- Acoplamiento (CBO) ≤ 5, Cohesión (LCOM) ≤ 1, Índice de mantenibilidad > 20
- Arquitectura: violaciones de capas = 0, ciclos de dependencias = 0

### Configuración de Herramientas

Todas las herramientas estandarizadas en `pyproject.toml`:
- **Black/isort:** line-length 100, perfil compatible con Black
- **Ruff:** reglas E, F, W, I, N, B, C4 (E501 ignorado)
- **mypy:** modo estricto, `disallow_untyped_defs = true`

### Parseo de TOML

Python 3.11+: `tomllib` incorporado. Python < 3.11: `tomli` (instalado condicionalmente via `pyproject.toml`).

## Fixtures de Tests

En `tests/conftest.py`:
- `temp_project` — Proyecto temporal con `src/sample.py`
- `sample_python_file` — Ruta al archivo Python de ejemplo
- `empty_config` — Instancia por defecto de `QualityConfig`

## Archivos de Referencia Clave

- `.dev/SESION.md` — **Leer al inicio de sesión** para contexto actual y seguimiento de tareas
- `docs/agentes/decision_arquitectura_checks_modulares.md` — Decisión de arquitectura modular (autoritativo)
- `docs/agentes/especificacion_agentes_calidad.md` — Especificación completa de agentes (v1.1)
- `docs/agentes/guia_implementacion_agentes.md` — Guía de implementación
- `docs/teoria/GUIA_REDACCION.md` — Estilo de redacción para docs de teoría
- `docs/guias/codeguard.md` — Guía de usuario de CodeGuard

## Decisiones Técnicas

- **IA:** Claude API (`claude-sonnet-4-20250514`)
- **CLI:** Click
- **Salida en consola:** Rich
- **Reportes:** Templates Jinja2
- **Dashboards:** Plotly (no Dash, no Streamlit)
- **Métricas históricas (ArchitectAnalyst):** SQLite

## Gestión de Sesión

El sistema de sesiones es automático via hooks (`SessionEnd` guarda, `SessionStart` verifica):
- Los archivos viven en `~/.claude/projects/-Users-victor-PycharmProjects-software-limpio/memory/`
- `/resume` — Restaurar contexto al inicio de una nueva sesión (lee commits, estado, próximos pasos)
