# Guía de Adopción — CodeGuard

> Cómo incorporar CodeGuard en proyectos existentes y nuevos

Esta guía cubre los dos escenarios más comunes de adopción. Para referencia completa de
todas las opciones, ver la [Guía de Usuario](codeguard.md).

---

## Índice

1. [Instalación](#instalación)
2. [Escenario A: Proyecto Existente](#escenario-a-proyecto-existente)
3. [Escenario B: Proyecto Nuevo](#escenario-b-proyecto-nuevo)
4. [Referencia de Configuración](#referencia-de-configuración)

---

## Instalación

### Desde la release oficial (recomendado)

```bash
pip install git+https://github.com/vvalotto/software_limpio.git@v0.1.0
```

### En modo desarrollo (para contribuir)

```bash
git clone https://github.com/vvalotto/software_limpio.git
cd software_limpio
pip install -e ".[dev]"
```

### Verificar

```bash
codeguard --help
```

---

## Escenario A: Proyecto Existente

El objetivo es agregar visibilidad de calidad sin interrumpir el flujo actual.
CodeGuard **nunca bloquea commits** — solo advierte.

### Paso 1: Primera corrida exploratoria

Sin configurar nada, corré CodeGuard sobre tu código para ver el estado real:

```bash
cd mi-proyecto
codeguard src/
```

Esto te da una línea de base. No te preocupes por la cantidad de advertencias al
principio — es información, no un bloqueo.

Para ver el detalle en JSON y guardarlo:

```bash
codeguard src/ --format json > calidad-baseline.json
```

### Paso 2: Configurar umbrales realistas

Agregá una sección `[tool.codeguard]` en tu `pyproject.toml`. Empezá con umbrales
más laxos que los defaults y ajustalos gradualmente a medida que mejorás el código:

```toml
[tool.codeguard]
# Umbrales iniciales para proyecto con deuda técnica
max_cyclomatic_complexity = 15   # default: 10 — empezar más permisivo
max_line_length = 120            # default: 100 — ajustar al estilo existente
min_pylint_score = 6.0           # default: 8.0 — bajar si el score actual es bajo

# Activar solo los checks que agreguen valor ahora
check_pep8 = true
check_security = true            # seguridad siempre activa
check_complexity = true
check_types = false              # desactivar si no hay type hints en el proyecto

# Excluir lo que no controlás
exclude_patterns = [
    "tests/*",
    "migrations/*",
    "venv/*",
    ".venv/*",
    "setup.py",
]
```

**Estrategia de mejora gradual:**

| Semana | Acción |
|--------|--------|
| 1-2 | Corrida exploratoria, configurar umbrales actuales |
| 3-4 | Activar `check_security`, resolver errores críticos |
| 5-8 | Bajar `max_cyclomatic_complexity` de a 1 por semana |
| 9+  | Activar `check_types`, agregar type hints progresivamente |

### Paso 3: Integrar con pre-commit (cuando el equipo esté listo)

```bash
pip install pre-commit
```

Crear `.pre-commit-config.yaml` en la raíz del proyecto:

```yaml
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.1.0
    hooks:
      - id: codeguard
        args: ['--analysis-type', 'pre-commit']
```

Activar para todos:

```bash
pre-commit install
```

A partir de ahí, CodeGuard corre automáticamente antes de cada `git commit`.

### Paso 4: Análisis más profundo antes de un PR

Para revisiones más exhaustivas antes de mergear:

```bash
codeguard src/ --analysis-type pr-review
```

Este modo activa todos los checks sin restricción de tiempo (~15-30s).

---

## Escenario B: Proyecto Nuevo

Acá tenés la ventaja de configurar todo bien desde el inicio.
El objetivo es que cada commit ya cumpla con los estándares.

### Paso 1: Configurar el proyecto base

```bash
mkdir mi-proyecto && cd mi-proyecto
git init
python -m venv .venv && source .venv/bin/activate
pip install git+https://github.com/vvalotto/software_limpio.git@v0.1.0
```

### Paso 2: Configuración estricta desde el inicio

En `pyproject.toml`:

```toml
[tool.codeguard]
# Umbrales estrictos — mantenerlos desde el día uno es mucho más fácil
max_cyclomatic_complexity = 10
max_line_length = 100
min_pylint_score = 8.0

# Todos los checks activos
check_pep8 = true
check_security = true
check_complexity = true
check_types = true        # type hints desde el primer módulo

exclude_patterns = [
    "tests/*",
    ".venv/*",
]
```

### Paso 3: Pre-commit desde el primer commit

```bash
pip install pre-commit
```

Crear `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.1.0
    hooks:
      # Análisis rápido en cada commit
      - id: codeguard
        args: ['--analysis-type', 'pre-commit']

  # Complementar con formateo automático (recomendado)
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        args: [--line-length=100]

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile, black, --line-length=100]
```

```bash
pre-commit install
```

### Paso 4: Verificar antes del primer commit real

```bash
# Crear tu primer archivo
mkdir src && touch src/__init__.py

# Verificar que CodeGuard pasa limpio
codeguard src/

# Si todo está bien, el primer commit ya tiene calidad garantizada
git add . && git commit -m "Initial commit"
```

---

## Referencia de Configuración

Todas las opciones disponibles en `[tool.codeguard]`:

```toml
[tool.codeguard]
# --- Checks activos ---
check_pep8 = true                # Estilo PEP8 (flake8)
check_security = true            # Vulnerabilidades (bandit)
check_complexity = true          # Complejidad ciclomática (radon)
check_types = true               # Tipos (mypy)
check_pylint = true              # Score general (pylint)
check_imports = true             # Imports sin usar (pylint)

# --- Umbrales ---
max_cyclomatic_complexity = 10   # Complejidad máxima por función
max_line_length = 100            # Longitud máxima de línea
min_pylint_score = 8.0           # Score mínimo de pylint (0-10)

# --- Exclusiones ---
exclude_patterns = [
    "tests/*",
    "migrations/*",
    ".venv/*",
]

# --- IA opcional (requiere API key de Anthropic) ---
[tool.codeguard.ai]
enabled = false
# api_key = "..."  # o usar variable de entorno ANTHROPIC_API_KEY
```

### Tipos de análisis

| Tipo | Tiempo | Cuándo usarlo |
|------|--------|---------------|
| `pre-commit` | < 5s | Automático en cada commit |
| `pr-review` | ~15s | Antes de abrir un PR |
| `full` | ~30s | Auditoría completa |

```bash
codeguard src/ --analysis-type pre-commit   # rápido
codeguard src/ --analysis-type pr-review    # completo
codeguard src/ --analysis-type full         # sin límites
```

### Formatos de salida

```bash
codeguard src/                      # texto con Rich (default)
codeguard src/ --format json        # JSON para pipelines/scripts
codeguard src/ --format json > out.json
```

---

## Comparación rápida

| | Proyecto existente | Proyecto nuevo |
|---|---|---|
| **Umbrales iniciales** | Laxos, ajustar gradualmente | Estrictos desde el inicio |
| **`check_types`** | Desactivar si no hay type hints | Activar desde el primer módulo |
| **Pre-commit** | Agregar cuando el equipo esté listo | Antes del primer commit |
| **Primera corrida** | Exploratoria, generar baseline | Debe dar 0 errores |
| **Estrategia** | Mejora gradual semana a semana | Mantener verde desde el día uno |

---

*Para más detalles: [Guía de Usuario Completa](codeguard.md)*
