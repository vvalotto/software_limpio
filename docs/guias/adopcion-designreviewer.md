# Guía de Adopción — DesignReviewer

> Cómo incorporar DesignReviewer en el flujo de PRs de proyectos existentes y nuevos

Esta guía cubre los dos escenarios más comunes de adopción. Para referencia completa de
todas las opciones, ver la [Guía de Usuario](designreviewer.md).

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
pip install git+https://github.com/vvalotto/software_limpio.git@v0.3.0
```

### En modo desarrollo (para contribuir)

```bash
git clone https://github.com/vvalotto/software_limpio.git
cd software_limpio
pip install -e ".[dev]"
```

### Verificar

```bash
designreviewer --help
```

---

## Escenario A: Proyecto Existente

El desafío principal al adoptar DesignReviewer en un proyecto con historia es que **puede bloquear PRs desde el primer día** si hay clases con problemas críticos. El objetivo es ganar visibilidad sin paralizar el equipo.

### Paso 1: Primera corrida exploratoria

Sin integrar nada a CI, corré DesignReviewer para ver el estado real:

```bash
cd mi-proyecto
designreviewer src/
```

Guardá el baseline en JSON para analizarlo:

```bash
designreviewer src/ --format json > diseno-baseline.json
```

Prestá atención a cuántos **BLOCKING ISSUES** aparecen. Si son muchos, empezar con los umbrales de la literatura (default) va a bloquear todos los PRs — lo que genera rechazo hacia la herramienta.

### Paso 2: Configurar umbrales realistas

Agregá `[tool.designreviewer]` en tu `pyproject.toml` con valores más permisivos que los defaults, basados en lo que viste en el baseline:

```toml
[tool.designreviewer]
# Ejemplo: proyecto con alto acoplamiento heredado
max_cbo = 10             # default: 5 — empezar más permisivo
max_wmc = 35             # default: 20 — ajustar si hay clases grandes
max_dit = 7              # default: 5 — common en frameworks con herencia profunda
max_fan_out = 12         # default: 7
max_lcom = 2             # default: 1

# Code smells: empezar desactivando critical, solo warnings
max_methods_per_class = 15     # default: 10 (warning)
max_methods_critical = 40      # default: 20 (critical) — muy permisivo al inicio
max_method_lines = 40          # default: 20 (warning)
max_method_lines_critical = 80 # default: 40 (critical)
max_parameters = 6             # default: 4 (warning)
max_parameters_critical = 10   # default: 7 (critical)
```

**Estrategia de mejora gradual:**

| Sprint | Acción |
|--------|--------|
| 1-2 | Corrida exploratoria, medir baseline, configurar umbrales actuales |
| 3-4 | Integrar a CI como informativo (`--no-ai`, revisar sin bloquear en un branch de prueba) |
| 5-6 | Bloquear solo CircularImports (siempre CRITICAL — cero tolerancia) |
| 7-8 | Bajar `max_cbo` y `max_wmc` hacia los valores recomendados de a uno |
| 9-12 | Continuar ajustando umbrales a medida que se paga deuda técnica |
| 13+ | Activar code smells críticos, acercarse a los defaults |

### Paso 3: Integrar al flujo de PRs (cuando el equipo esté listo)

Una vez que los umbrales configurados no generan falsos bloqueos, integrar a GitHub Actions:

```yaml
# .github/workflows/design-review.yml
name: Design Review

on: [pull_request]

jobs:
  design-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - name: Ejecutar DesignReviewer
        run: designreviewer src/
```

DesignReviewer usa el exit code para bloquear: si hay violaciones CRITICAL, el job falla y el PR queda bloqueado.

### Paso 4: Análisis solo del delta del PR

Para reducir ruido, analizá solo los archivos modificados en cada PR:

```bash
# En el workflow de GitHub Actions
FILES=$(git diff --name-only origin/main...HEAD -- '*.py')
if [ -n "$FILES" ]; then
    designreviewer $FILES
fi
```

Esto evita bloquear un PR por deuda técnica preexistente en archivos que no fueron tocados.

---

## Escenario B: Proyecto Nuevo

Acá tenés la ventaja de configurar todo bien desde el inicio.
El objetivo es que cada PR cumpla con los estándares de diseño desde el primer merge.

### Paso 1: Configuración estricta desde el inicio

En `pyproject.toml`, usá los defaults o incluso más estrictos:

```toml
[tool.designreviewer]
# Defaults de la literatura — mantenerlos desde el día uno es mucho más fácil
max_cbo = 5
max_fan_out = 7
max_lcom = 1
max_wmc = 20
max_dit = 5
max_nop = 1

# Code smells
max_methods_per_class = 10
max_methods_critical = 20
max_method_lines = 20
max_method_lines_critical = 40
max_parameters = 4
max_parameters_critical = 7
```

### Paso 2: Verificar que el proyecto base pasa limpio

Antes de integrar al flujo de PRs, corré DesignReviewer sobre el estado inicial:

```bash
designreviewer src/
# Debe retornar exit code 0 y 0 BLOCKING ISSUES
```

Si el scaffolding inicial ya tiene violaciones (frameworks con clases base, decoradores, etc.), ajustá los umbrales antes de continuar.

### Paso 3: Integrar a GitHub Actions desde el primer PR

```yaml
# .github/workflows/design-review.yml
name: Design Review

on: [pull_request]

jobs:
  design-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - name: Ejecutar DesignReviewer
        run: designreviewer src/
```

A partir de ahí, cada PR que introduzca una violación CRITICAL queda bloqueado automáticamente.

### Paso 4: Analizar antes del primer merge real

```bash
# Crear tu primer módulo
mkdir src/domain && touch src/domain/__init__.py src/domain/entity.py

# Verificar que DesignReviewer pasa limpio
designreviewer src/

# Si todo está bien, el primer PR ya tiene diseño garantizado
```

---

## Referencia de Configuración

Todas las opciones disponibles en `[tool.designreviewer]`:

```toml
[tool.designreviewer]
# --- Acoplamiento ---
max_cbo = 5              # CBO > 5 → CRITICAL
max_fan_out = 7          # Fan-Out > 7 → WARNING

# --- Cohesión y herencia ---
max_lcom = 1             # LCOM > 1 → WARNING
max_wmc = 20             # WMC > 20 → CRITICAL
max_dit = 5              # DIT > 5 → CRITICAL
max_nop = 1              # NOP > 1 → CRITICAL

# --- Code Smells ---
max_methods_per_class = 10     # God Object → WARNING
max_methods_critical = 20      # God Object → CRITICAL
max_method_lines = 20          # Long Method → WARNING
max_method_lines_critical = 40 # Long Method → CRITICAL
max_parameters = 4             # Long Parameter List → WARNING
max_parameters_critical = 7    # Long Parameter List → CRITICAL

# --- Exclusiones ---
exclude_patterns = [
    "tests/",
    "migrations/",
    "__pycache__/",
    ".venv/",
]
```

### Comparación de perfiles

| | Proyecto existente | Proyecto nuevo |
|---|---|---|
| **Umbrales iniciales** | Permisivos, ajustar gradualmente | Estrictos (defaults) desde el inicio |
| **CircularImports** | Siempre CRITICAL — cero tolerancia | Siempre CRITICAL |
| **Integración a CI** | Después de configurar umbrales | Antes del primer PR |
| **Análisis de archivos** | Solo delta del PR (evitar bloqueos por deuda previa) | Directorio completo |
| **Estrategia** | Mejora gradual sprint a sprint | Mantener verde desde el día uno |

---

*Para más detalles: [Guía de Usuario Completa](designreviewer.md)*
