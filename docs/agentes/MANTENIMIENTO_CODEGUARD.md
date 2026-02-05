# Guía de Mantenimiento - CodeGuard

> Documentación técnica para mantenimiento y evolución a largo plazo

**Audiencia:** Desarrolladores que necesitan mantener, debuggear o evolucionar CodeGuard.

**Última actualización:** 2026-02-05

---

## Índice

1. [Arquitectura Interna](#arquitectura-interna)
2. [Decisiones de Diseño](#decisiones-de-diseño)
3. [Debugging y Troubleshooting](#debugging-y-troubleshooting)
4. [Actualización de Dependencias](#actualización-de-dependencias)
5. [Performance y Optimización](#performance-y-optimización)
6. [Roadmap Técnico](#roadmap-técnico)
7. [Breaking Changes](#breaking-changes)

---

## Arquitectura Interna

### Diagrama de Flujo

```
Usuario ejecuta: codeguard .
         ↓
    CLI (agent.py:main)
         ↓
    load_config() → pyproject.toml o .codeguard.yml
         ↓
    CodeGuard.__init__(config)
         ↓
    CheckOrchestrator.__init__(config)
         ↓
    orchestrator._discover_checks() → Auto-discovery
         ↓
    CodeGuard.run(paths, analysis_type, time_budget)
         ↓
    Para cada archivo:
        ├─ Crear ExecutionContext
        ├─ orchestrator.select_checks(context)
        ├─ Para cada check seleccionado:
        │    ├─ check.should_run(context)
        │    └─ check.execute(file_path)
        └─ Acumular CheckResults
         ↓
    format_results(results) → Rich formatter
         ↓
    Exit code (0 = sin errores críticos)
```

### Ciclo de Vida de un Check

```python
# 1. DISCOVERY (orchestrator._discover_checks)
checks_module = importlib.import_module("quality_agents.codeguard.checks")
for name in dir(checks_module):
    obj = getattr(checks_module, name)
    if isinstance(obj, type) and issubclass(obj, Verifiable):
        checks.append(obj())

# 2. SELECTION (orchestrator.select_checks)
selected = []
for check in self.checks:
    if check.should_run(context):
        selected.append(check)
selected.sort(key=lambda c: c.priority)

# 3. EXECUTION (CodeGuard.run)
for check in selected_checks:
    try:
        results += check.execute(file_path)
    except Exception as e:
        results.append(CheckResult(ERROR, f"{check.name} failed"))

# 4. FORMATTING (formatter.format_results)
group_by_severity(results)
create_rich_tables()
show_suggestions()
```

---

## Decisiones de Diseño

### 1. ¿Por qué Auto-Discovery en lugar de Registro Manual?

**Decisión:** Usar auto-discovery con `importlib` + `inspect`

**Ventajas:**
- ✅ Agregar checks nuevos es trivial (crear clase + exportar)
- ✅ No se requiere modificar archivos core
- ✅ Reduce acoplamiento
- ✅ Facilita testing aislado de checks

**Desventajas:**
- ❌ Ligeramente más lento en startup (~50ms overhead)
- ❌ Más difícil de debuggear si falla el import

**Trade-off:** Preferimos DX (developer experience) sobre 50ms de startup.

**Implementación:**

```python
# orchestrator.py:42-68
def _discover_checks(self) -> List[Verifiable]:
    """Auto-discover all check classes from checks module."""
    checks = []
    checks_module = importlib.import_module("quality_agents.codeguard.checks")

    for name in dir(checks_module):
        if name.startswith("_"):
            continue
        obj = getattr(checks_module, name)
        if isinstance(obj, type) and issubclass(obj, Verifiable) and obj is not Verifiable:
            try:
                check_instance = obj()
                checks.append(check_instance)
            except Exception as e:
                logger.warning(f"Failed to instantiate {name}: {e}")

    return sorted(checks, key=lambda c: c.priority)
```

### 2. ¿Por qué Orquestación Contextual en lugar de "Todos o Nada"?

**Decisión:** Orquestador selecciona checks según contexto

**Problema original:**
- Pre-commit necesita < 5s, pero algunos checks tardan 3s
- Usuarios querían control granular sin configuración compleja

**Solución:**
- Priority system (1-6)
- Analysis types (pre-commit, pr-review, full)
- Time budgets opcionales

**Código clave:**

```python
# orchestrator.py:70-140
def select_checks(self, context: ExecutionContext) -> List[Verifiable]:
    """Select checks based on context."""
    selected = []

    for check in self.checks:
        # Verificar exclusión
        if context.is_excluded:
            continue

        # Verificar si debe ejecutarse
        if not check.should_run(context):
            continue

        # Verificar presupuesto de tiempo
        if context.time_budget is not None:
            if self._get_used_time(selected) + check.estimated_duration > context.time_budget:
                break

        selected.append(check)

    return selected
```

### 3. ¿Por qué pyproject.toml en lugar de solo YAML?

**Decisión:** pyproject.toml como opción primaria, YAML como fallback

**Razones:**
- PEP 518 es el estándar moderno de Python
- Un solo archivo para todas las herramientas (black, pytest, mypy, etc.)
- Mejor soporte en IDEs
- Ecosistema Python se está moviendo hacia TOML

**Implementación:**

```python
# config.py:195-225
def load_config(config_path=None, project_root=None):
    # Priority 1: Explicit CLI arg
    if config_path:
        return CodeGuardConfig.from_yaml(config_path)

    # Priority 2: pyproject.toml
    if project_root:
        pyproject = project_root / "pyproject.toml"
        if pyproject.exists():
            return CodeGuardConfig.from_pyproject_toml(pyproject)

    # Priority 3: .codeguard.yml
    yml_paths = [
        project_root / ".codeguard.yml" if project_root else Path(".codeguard.yml"),
        Path("configs/codeguard.yml"),
    ]
    for yml in yml_paths:
        if yml.exists():
            return CodeGuardConfig.from_yaml(yml)

    # Priority 4: Defaults
    return CodeGuardConfig()
```

### 4. ¿Por qué Rich en lugar de output simple?

**Decisión:** Usar Rich para formateo profesional

**Razones:**
- Mejor UX (tablas, colores, iconos)
- Sugerencias contextuales más claras
- Output JSON no afectado (modo --format json)
- Degradación graceful en terminals sin color

**Trade-off:**
- Dependencia adicional (~500KB)
- Requiere terminal compatible

**Mitigación:**
- Flag `--no-color` para terminals básicos
- Modo JSON para CI/CD

---

## Debugging y Troubleshooting

### Problema 1: Check No Se Ejecuta

**Síntomas:** Check aparece en discovery pero no se ejecuta.

**Debugging:**

```bash
# Activar logging detallado
export CODEGUARD_DEBUG=1
codeguard . --verbose

# Ver qué checks se descubrieron
python3 << EOF
from quality_agents.codeguard.orchestrator import CheckOrchestrator
from quality_agents.codeguard.config import load_config

config = load_config()
orch = CheckOrchestrator(config)
for check in orch.checks:
    print(f"{check.name}: priority={check.priority}, duration={check.estimated_duration}s")
EOF
```

**Causas comunes:**
1. `should_run()` retorna `False`
2. Prioridad muy baja + presupuesto de tiempo agotado
3. Archivo excluido por `exclude_patterns`

**Solución:**
```python
# Verificar should_run() del check
context = ExecutionContext(
    file_path=Path("test.py"),
    analysis_type="pre-commit",
    config=config,
    is_excluded=False
)
print(check.should_run(context))  # ¿True o False?
```

### Problema 2: Auto-Discovery Falla

**Síntomas:** Error al importar módulo de checks.

**Debugging:**

```bash
# Verificar que el check está exportado
python3 << EOF
from quality_agents.codeguard import checks
print(checks.__all__)  # ¿Está tu check listado?
EOF

# Verificar import directo
python3 -c "from quality_agents.codeguard.checks import MiCheck"
```

**Causas comunes:**
1. Check no exportado en `checks/__init__.py`
2. Errores de sintaxis en el check
3. Dependencias faltantes

**Solución:**
```python
# checks/__init__.py
from .mi_check import MiCheck

__all__ = [
    # ... otros ...
    "MiCheck",  # ← AGREGAR AQUÍ
]
```

### Problema 3: Performance Degradada

**Síntomas:** CodeGuard tarda más de 5s en pre-commit.

**Debugging:**

```bash
# Medir tiempo de cada check
codeguard . --format json | jq '.results | group_by(.check_name) | map({check: .[0].check_name, count: length})'

# Profiling
python3 -m cProfile -o codeguard.prof $(which codeguard) .
python3 -m pstats codeguard.prof
```

**Causas comunes:**
1. Check con `estimated_duration` incorrecto
2. Muchos archivos grandes
3. Herramientas externas lentas (mypy, pylint)

**Solución:**
```python
# Ajustar prioridad o estimated_duration
@property
def priority(self) -> int:
    return 5  # Mover a pr-review en lugar de pre-commit

@property
def estimated_duration(self) -> float:
    return 3.0  # Ajustar si medimos que tarda más
```

### Problema 4: Rich Formatter Roto en CI/CD

**Síntomas:** Output ilegible en pipelines CI/CD.

**Solución:**

```yaml
# GitHub Actions / GitLab CI
- name: Run CodeGuard
  run: codeguard --format json --no-color . > report.json
```

O detectar automáticamente:

```python
# formatter.py
import sys

def format_results(results, execution_time):
    if not sys.stdout.isatty():
        # CI/CD detected, usar output simple
        format_simple(results)
    else:
        # Terminal interactivo, usar Rich
        format_rich(results)
```

---

## Actualización de Dependencias

### Dependencias Core

```toml
[project]
dependencies = [
    "click>=8.0",           # CLI framework
    "rich>=13.0",           # Rich formatter
    "flake8>=7.0",          # PEP8 check
    "pylint>=3.0",          # Code quality
    "bandit>=1.7",          # Security
    "radon>=6.0",           # Complexity
    "mypy>=1.8",            # Type checking
    "tomli>=2.0; python_version<'3.11'",  # TOML parser
]
```

### Proceso de Actualización

```bash
# 1. Actualizar dependencias en pyproject.toml
vim pyproject.toml  # Actualizar versiones

# 2. Reinstalar
pip install -e ".[dev]" --upgrade

# 3. Ejecutar tests completos
pytest

# 4. Verificar manualmente
codeguard . --analysis-type full

# 5. Actualizar constraints si es necesario
pip freeze > constraints.txt
```

### Breaking Changes a Vigilar

#### flake8
- **v6 → v7:** Cambios en formato de output (verificar parseo en `pep8_check.py`)

#### pylint
- **v2 → v3:** Nuevos mensajes, deprecación de algunos checkers

#### mypy
- **Cada minor:** Nuevas reglas de tipo (puede romper TypeCheck)

#### Rich
- **v12 → v13:** Cambios en API de tablas

**Mitigación:**
- Pin versiones en producción: `rich==13.7.0`
- Tests de regresión para cada check
- CI/CD que falla si output cambia inesperadamente

---

## Performance y Optimización

### Benchmarks Actuales

| Check | Tiempo (avg) | Bottleneck |
|-------|--------------|------------|
| PEP8Check | 0.5s | flake8 subprocess |
| SecurityCheck | 1.5s | bandit JSON parsing |
| ComplexityCheck | 1.0s | radon analysis |
| PylintCheck | 2.0s | pylint full analysis |
| TypeCheck | 3.0s | mypy type inference |
| ImportCheck | 0.5s | pylint --disable=all |

**Total (full):** ~8.5s para proyecto mediano (20 archivos)

### Optimizaciones Implementadas

#### 1. Lazy Import de Herramientas

```python
# MALO: Import al inicio
import subprocess
from pylint import lint

# BUENO: Import en execute()
def execute(self, file_path):
    import subprocess  # Solo si se ejecuta
    result = subprocess.run(...)
```

#### 2. Caché de Resultados (Futuro)

```python
# IMPLEMENTAR: Caché basado en hash de archivo
def execute(self, file_path):
    file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
    cached = self.cache.get(file_hash)
    if cached:
        return cached
    # ... ejecutar check ...
    self.cache.set(file_hash, results)
```

#### 3. Paralelización (Futuro)

```python
# IMPLEMENTAR: Ejecutar checks en paralelo
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(check.execute, file_path) for check in checks]
    results = [f.result() for f in futures]
```

**Trade-off:** Debugging más difícil, race conditions potenciales.

### Profiling

```bash
# Profile completo
python3 -m cProfile -o codeguard.prof -s cumulative $(which codeguard) .

# Analizar
python3 << EOF
import pstats
p = pstats.Stats('codeguard.prof')
p.sort_stats('cumulative')
p.print_stats(20)  # Top 20 funciones
EOF

# Visualizar con snakeviz
pip install snakeviz
snakeviz codeguard.prof
```

---

## Roadmap Técnico

### Corto Plazo (v0.2.0 - v0.3.0)

- [ ] **Caché de resultados** (hashmap file → results)
- [ ] **Paralelización de checks** (ThreadPoolExecutor)
- [ ] **IA opcional con Claude** (Fase 3 completa)
- [ ] **Modo incremental** (solo archivos modificados desde último commit)
- [ ] **Plugin system** (checks externos sin modificar código core)

### Mediano Plazo (v0.4.0 - v0.6.0)

- [ ] **Dashboard web** (Flask + D3.js para visualización)
- [ ] **Histórico de métricas** (SQLite tracking de evolución)
- [ ] **Auto-fix sugerencias** (aplicar correcciones automáticamente)
- [ ] **IDE integration** (VS Code extension)

### Largo Plazo (v1.0.0+)

- [ ] **Language Server Protocol** (LSP server para linting en tiempo real)
- [ ] **Machine Learning** (aprender de correcciones aceptadas/rechazadas)
- [ ] **Multi-language support** (JavaScript, TypeScript, Go)

---

## Breaking Changes

### Versioning Policy

Seguimos [Semantic Versioning](https://semver.org/):

- **MAJOR (1.0.0):** Breaking changes en API pública
- **MINOR (0.1.0):** Nuevas features, backward compatible
- **PATCH (0.0.1):** Bug fixes

### Registro de Breaking Changes

#### v0.1.0 → v0.2.0 (Planeado)

**BC1: Cambio en estructura de ExecutionContext**

```python
# v0.1.0
ExecutionContext(file_path, analysis_type, config, is_excluded)

# v0.2.0 (planeado)
ExecutionContext(
    file_path,
    analysis_type,
    config,
    is_excluded,
    file_hash: str,  # NUEVO: para caché
    last_modified: float  # NUEVO: para incremental
)
```

**Mitigación:** Mantener constructor compatible con kwargs.

**BC2: Cambio en formato JSON de output**

```json
// v0.1.0
{"results": [...], "summary": {...}}

// v0.2.0 (planeado)
{
  "version": "0.2.0",
  "results": [...],
  "summary": {...},
  "cache_stats": {...}  // NUEVO
}
```

**Mitigación:** Agregar `"version"` key, consumers deben validar.

---

## Contacto para Mantenimiento

**Maintainer Actual:** Víctor Valotto

**Issues:** https://github.com/vvalotto/software_limpio/issues

**Documentación Relacionada:**
- [Decisión Arquitectura Modular](decision_arquitectura_checks_modulares.md)
- [Guía de Implementación](guia_implementacion_agentes.md)
- [README Técnico](../../src/quality_agents/codeguard/README.md)

---

**Última revisión:** 2026-02-05
**Próxima revisión programada:** Cada release major/minor
