# CodeGuard - Agente de Control de Calidad de Código

> Análisis de calidad rápido y modular para Python

**CodeGuard** es el primer agente del framework Software Limpio, diseñado para ejecutarse en pre-commit (< 5s) y detectar problemas de calidad, seguridad y estilo en código Python.

---

## Características Principales

- ✅ **6 Checks Modulares** - PEP8, Security, Complexity, Pylint, Types, Imports
- ✅ **Orquestación Contextual** - Adapta qué checks ejecuta según contexto
- ✅ **Rich Formatter** - Output profesional con colores y tablas
- ✅ **Configuración Moderna** - pyproject.toml (PEP 518) + fallback YAML
- ✅ **Pre-commit Framework** - Integración estándar con 3 hooks
- ✅ **Rápido** - < 5 segundos en modo pre-commit
- ⏳ **IA Opcional** - Sugerencias inteligentes con Claude API (opt-in)

---

## Arquitectura

### Estructura de Directorios

```
src/quality_agents/codeguard/
├── agent.py              # CLI principal y coordinación
├── config.py             # Configuración (pyproject.toml/YAML)
├── orchestrator.py       # Orquestador contextual con auto-discovery
├── formatter.py          # Rich formatter + JSON output
├── checks/               # Checks modulares (patrón Verifiable)
│   ├── __init__.py       # Exports de todos los checks
│   ├── pep8_check.py     # PEP8 style (flake8)
│   ├── security_check.py # Security vulnerabilities (bandit)
│   ├── complexity_check.py # Cyclomatic complexity (radon)
│   ├── pylint_check.py   # Code quality (pylint)
│   ├── type_check.py     # Type checking (mypy)
│   └── import_check.py   # Unused imports (pylint)
└── PLAN_IMPLEMENTACION.md # Roadmap completo
```

### Componentes Clave

#### 1. Agent (agent.py)

Punto de entrada CLI y coordinador principal:

```python
class CodeGuard:
    def __init__(self, config: Optional[CodeGuardConfig] = None):
        self.config = config or load_config()
        self.orchestrator = CheckOrchestrator(self.config)

    def run(
        self,
        file_paths: List[Path],
        analysis_type: str = "pre-commit",
        time_budget: Optional[float] = None
    ) -> List[CheckResult]:
        # Crea ExecutionContext para cada archivo
        # Orquestador selecciona checks
        # Ejecuta checks y retorna resultados
```

#### 2. Orchestrator (orchestrator.py)

Selecciona qué checks ejecutar según contexto:

```python
class CheckOrchestrator:
    def __init__(self, config: CodeGuardConfig):
        self.config = config
        self.checks = self._discover_checks()  # Auto-discovery

    def select_checks(self, context: ExecutionContext) -> List[Verifiable]:
        # Filtra por analysis_type, time_budget, prioridad
        # Retorna lista ordenada de checks a ejecutar
```

**Estrategias de selección:**
- `pre-commit`: Solo checks con priority 1-3 (< 5s)
- `pr-review`: Checks con priority 1-5 (~10-15s)
- `full`: Todos los checks (~20-30s)

#### 3. Checks Modulares (checks/)

Todos heredan de `Verifiable` (patrón base):

```python
from quality_agents.shared.verifiable import Verifiable, ExecutionContext
from pathlib import Path
from typing import List

class PEP8Check(Verifiable):
    @property
    def name(self) -> str:
        return "PEP8Check"

    @property
    def priority(self) -> int:
        return 2  # 1 = más crítico

    @property
    def estimated_duration(self) -> float:
        return 0.5  # segundos

    def should_run(self, context: ExecutionContext) -> bool:
        # Decide si ejecutarse según contexto
        if context.is_excluded:
            return False
        if context.analysis_type == "pre-commit":
            return self.priority <= 3
        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        # Implementación del check (flake8)
        results = []
        # ... lógica ...
        return results
```

#### 4. Configuration (config.py)

Carga configuración desde pyproject.toml o YAML:

```python
@dataclass
class CodeGuardConfig:
    min_pylint_score: float = 8.0
    max_cyclomatic_complexity: int = 10
    check_pep8: bool = True
    # ... más opciones ...
    ai: AIConfig = field(default_factory=AIConfig)

def load_config(
    config_path: Optional[Path] = None,
    project_root: Optional[Path] = None
) -> CodeGuardConfig:
    # Búsqueda automática: CLI arg → pyproject.toml → .yml → defaults
```

#### 5. Formatter (formatter.py)

Output profesional con Rich:

```python
def format_results(
    results: List[CheckResult],
    execution_time: float
) -> None:
    # Crea tablas con Rich
    # Agrupa por severidad
    # Muestra sugerencias contextuales
```

---

## Agregar un Nuevo Check

### Paso 1: Crear el Check

Crear archivo `checks/mi_check.py`:

```python
from quality_agents.shared.verifiable import Verifiable, ExecutionContext
from quality_agents.codeguard.agent import CheckResult, Severity
from pathlib import Path
from typing import List

class MiCheck(Verifiable):
    """Descripción del check."""

    @property
    def name(self) -> str:
        return "MiCheck"

    @property
    def category(self) -> str:
        return "code_quality"

    @property
    def priority(self) -> int:
        return 4  # 1 = más crítico, 6 = menos crítico

    @property
    def estimated_duration(self) -> float:
        return 1.5  # segundos estimados

    def should_run(self, context: ExecutionContext) -> bool:
        """Decide si este check debe ejecutarse."""
        if context.is_excluded:
            return False

        # Solo en análisis completo
        if context.analysis_type == "full":
            return True

        return False

    def execute(self, file_path: Path) -> List[CheckResult]:
        """Ejecuta la verificación."""
        results = []

        # Implementar lógica del check aquí
        # Ejemplo: ejecutar herramienta externa
        try:
            # subprocess.run(...) o análisis directo
            # Si encuentra problemas:
            results.append(CheckResult(
                check_name=self.name,
                severity=Severity.WARNING,
                message="Problema detectado",
                file_path=str(file_path),
                line_number=42
            ))
        except Exception as e:
            # Manejar errores
            pass

        return results
```

### Paso 2: Exportar el Check

En `checks/__init__.py`:

```python
from .pep8_check import PEP8Check
from .security_check import SecurityCheck
# ... otros checks ...
from .mi_check import MiCheck  # NUEVO

__all__ = [
    "PEP8Check",
    "SecurityCheck",
    # ...
    "MiCheck",  # NUEVO
]
```

### Paso 3: ¡Listo!

**Auto-discovery** detecta el nuevo check automáticamente. No se requiere modificar `orchestrator.py` ni `agent.py`.

```bash
# Probar el nuevo check
codeguard --analysis-type full .
```

---

## Orquestación Contextual

El orquestador decide qué checks ejecutar basándose en:

### 1. Tipo de Análisis

| Tipo | Checks | Uso |
|------|--------|-----|
| `pre-commit` | Priority 1-3 | Commits rápidos |
| `pr-review` | Priority 1-5 | Pull requests |
| `full` | Priority 1-6 | Análisis exhaustivo |

### 2. Presupuesto de Tiempo

```bash
codeguard --time-budget 3.0 .
```

Ejecuta checks ordenados por prioridad hasta agotar el presupuesto.

### 3. Estado del Archivo

```python
class ExecutionContext:
    file_path: Path
    analysis_type: str
    time_budget: Optional[float]
    config: CodeGuardConfig
    is_excluded: bool          # Según exclude_patterns
    file_age: Optional[float]  # Para priorizar archivos nuevos
    ai_enabled: bool           # Si IA está habilitada
```

### 4. Prioridades de Checks

1. **SecurityCheck** - Vulnerabilidades críticas
2. **PEP8Check** - Estilo básico
3. **ComplexityCheck** - Complejidad ciclomática
4. **PylintCheck** - Calidad general
5. **TypeCheck** - Type hints
6. **ImportCheck** - Imports sin usar

---

## Testing

### Ejecutar Tests

```bash
# Todos los tests de CodeGuard
pytest tests/unit/test_codeguard*.py tests/unit/test_*_check.py -v

# Tests de integración
pytest tests/integration/test_codeguard_integration.py -v

# Tests end-to-end
pytest tests/e2e/test_codeguard_e2e.py -v

# Coverage
pytest --cov=src/quality_agents/codeguard --cov-report=html
```

### Estructura de Tests

```
tests/
├── unit/
│   ├── test_codeguard.py            # Agent principal
│   ├── test_codeguard_config.py     # Configuración
│   ├── test_orchestrator.py         # Orquestador
│   ├── test_formatter.py            # Formatters
│   ├── test_pep8_check.py           # Checks individuales
│   ├── test_security_check.py
│   └── ...
├── integration/
│   ├── test_codeguard_integration.py  # Integración completa
│   └── test_pre_commit_hooks.py       # Pre-commit framework
└── e2e/
    └── test_codeguard_e2e.py          # End-to-end con CLI
```

---

## Configuración

### pyproject.toml (Recomendado)

```toml
[tool.codeguard]
min_pylint_score = 8.0
max_cyclomatic_complexity = 10
check_pep8 = true
check_security = true
exclude_patterns = ["tests/*", "migrations/*"]

[tool.codeguard.ai]
enabled = false
```

### YAML (Fallback)

```yaml
# .codeguard.yml
min_pylint_score: 8.0
max_cyclomatic_complexity: 10
check_pep8: true
exclude_patterns:
  - "tests/*"
```

---

## Documentación

### Para Usuarios

- **[Guía de Usuario](../../docs/guias/codeguard.md)** - Instalación, uso, configuración, FAQ
- **[README Principal](../../README.md)** - Quick start del proyecto

### Para Desarrolladores

- **[Decisión Arquitectónica](../../docs/agentes/decision_arquitectura_checks_modulares.md)** - Sistema modular
- **[Guía de Implementación](../../docs/agentes/guia_implementacion_agentes.md)** - Patrones y estructura
- **[Especificación Técnica](../../docs/agentes/especificacion_agentes_calidad.md)** - Specs completas
- **[Mantenimiento](../../docs/agentes/MANTENIMIENTO_CODEGUARD.md)** - Cómo mantener y extender

### Roadmap

- **[Plan de Implementación](PLAN_IMPLEMENTACION.md)** - Fases, tickets, progreso

---

## Estado Actual

**Version:** 0.1.0 (MVP)

### Completado ✅

- [x] Arquitectura modular con patrón Verifiable
- [x] 6 checks implementados y probados
- [x] Orquestación contextual
- [x] Rich formatter profesional
- [x] Configuración vía pyproject.toml
- [x] Pre-commit framework (3 hooks)
- [x] 300 tests pasando (100%)
- [x] Documentación completa

### En Progreso ⏳

- [ ] Fase 3: IA opcional con Claude API

### Próximos Pasos 🔜

1. Release v0.1.0
2. Feedback de usuarios
3. Optimizaciones de performance
4. Más checks modulares (coverage, docstrings, etc.)

---

## Contribuir

1. **Fork** el repositorio
2. **Crear branch** (`git checkout -b feature/mi-check`)
3. **Implementar** siguiendo el patrón Verifiable
4. **Tests** (100% coverage esperado)
5. **Pull Request** con descripción detallada

Ver [Guía de Implementación](../../docs/agentes/guia_implementacion_agentes.md) para más detalles.

---

## Licencia

MIT - Ver [LICENSE](../../LICENSE)

---

## Autor

Víctor Valotto - FIUNER

**Software Limpio** - Framework de Control de Calidad para Python
