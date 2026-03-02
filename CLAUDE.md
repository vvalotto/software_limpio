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

# Ejecutar todos los tests (~766 tests, ~30s)
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
codeguard --config examples/configs/codeguard.yml # Configuración personalizada

designreviewer src/                      # Análisis de diseño (bloquea si hay CRITICAL)
designreviewer src/ --format json        # Salida en JSON

architectanalyst src/                    # Análisis de arquitectura (solo informa, no bloquea)
architectanalyst src/ --sprint-id sprint-12  # Con ID de sprint para tracking
architectanalyst src/ --format json      # Salida en JSON
```

## Arquitectura

Sistema de control de calidad en tres niveles:

```
Pre-commit (<5s)    →    PR Review (2-5min)    →    Fin de Sprint (10-30min)
      ↓                        ↓                           ↓
  CodeGuard              DesignReviewer             ArchitectAnalyst
 (solo advierte)       (bloquea si crítico)        (análisis de tendencias)
```

Los **tres agentes están implementados** (v0.3.0): CodeGuard (v0.1.0), DesignReviewer (v0.2.0), ArchitectAnalyst (v0.3.0). La integración IA es opt-in y está pendiente para v0.4.0.

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

Los tres agentes usan `[tool.<agente>]` en `pyproject.toml`:
- `[tool.codeguard]` — con fallback a `.codeguard.yml`
- `[tool.designreviewer]`
- `[tool.architectanalyst]` — incluye sección `[tool.architectanalyst.layers]` opcional

### Configuración de Herramientas

Todas las herramientas estandarizadas en `pyproject.toml`:
- **Black/isort:** line-length 100, perfil compatible con Black
- **Ruff:** reglas E, F, W, I, N, B, C4 (E501 ignorado)
- **mypy:** modo estricto, `disallow_untyped_defs = true`

## Fixtures de Tests

En `tests/conftest.py`:
- `temp_project` — Proyecto temporal con `src/sample.py`
- `sample_python_file` — Ruta al archivo Python de ejemplo
- `empty_config` — Instancia por defecto de `QualityConfig`

## Archivos de Referencia Clave

- `docs/agentes/especificacion_agentes_calidad.md` — Especificación completa de agentes (v1.3, autoritativo)
- `docs/agentes/arquitectura_modular.md` — Decisión de arquitectura modular
- `docs/teoria/GUIA_REDACCION.md` — Estilo de redacción para docs de teoría
- `docs/guias/codeguard.md` — Guía de usuario de CodeGuard
- `docs/guias/designreviewer.md` — Guía de usuario de DesignReviewer
- `docs/guias/architectanalyst.md` — Guía de usuario de ArchitectAnalyst
- `gestion/backlog.md` — Features pendientes por versión

## Decisiones Técnicas

- **IA:** Claude API (`claude-sonnet-4-20250514`) — opt-in, pendiente v0.4.0
- **CLI:** Click
- **Salida en consola:** Rich
- **Reportes JSON:** Jinja2 (en DesignReviewer reporters.py)
- **Métricas históricas (ArchitectAnalyst):** SQLite en `.quality_control/architecture.db`

## Gestión de Sesión

El sistema de sesiones es automático via hooks (`SessionEnd` guarda, `SessionStart` verifica):
- Los archivos viven en `~/.claude/projects/-Users-victor-PycharmProjects-software-limpio/memory/`
- `/resume` — Restaurar contexto al inicio de una nueva sesión (lee commits, estado, próximos pasos)
