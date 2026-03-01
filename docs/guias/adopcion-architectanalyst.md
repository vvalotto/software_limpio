# Guía de Adopción — ArchitectAnalyst

> Cómo incorporar ArchitectAnalyst en el ritmo de sprints de proyectos existentes y nuevos

Esta guía cubre los dos escenarios más comunes de adopción. Para referencia completa de
todas las opciones, ver la [Guía de Usuario](architectanalyst.md).

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
architectanalyst --help
```

---

## Escenario A: Proyecto Existente

A diferencia de CodeGuard y DesignReviewer, ArchitectAnalyst **nunca bloquea** — el
exit code es siempre 0. Esto hace que la adopción sea más sencilla: no hay riesgo de
interrumpir el flujo del equipo desde el primer día.

El principal desafío es distinto: **el valor de ArchitectAnalyst está en las tendencias**,
no en el valor puntual de una métrica. Los primeros análisis mostrarán "—" en las tendencias
hasta acumular histórico.

### Paso 1: Primera corrida exploratoria

Sin configurar nada, corré ArchitectAnalyst para ver el estado arquitectónico actual:

```bash
cd mi-proyecto
architectanalyst src/ --sprint-id baseline
```

Guardá el baseline en JSON para tener la referencia inicial:

```bash
architectanalyst src/ --sprint-id baseline --format json > arquitectura-baseline.json
```

Prestá atención a:
- **Ciclos de dependencias**: si ya existen, son CRITICAL y deben resolverse
- **Módulos con D alto (> 0.5)**: candidatos a refactoring
- **Módulos con I alto (> 0.8)**: inestables — cambiarlos tiene alto riesgo

### Paso 2: Configurar el proyecto

Agregá `[tool.architectanalyst]` en tu `pyproject.toml`. Los defaults son buenos puntos
de partida — el foco es configurar las exclusiones y, opcionalmente, las capas:

```toml
[tool.architectanalyst]
# Umbrales — los defaults están bien para empezar
max_instability = 0.8       # I > 0.8 → WARNING
max_distance_warning = 0.3  # D > 0.3 → WARNING
max_distance_critical = 0.5 # D > 0.5 → CRITICAL

# Ajustar según tu estructura de directorios
exclude_patterns = [
    "__pycache__",
    ".venv",
    "migrations",
    "tests",
    "dist",
    "build",
    "docs",
]

# Capas (opcional — activar cuando la arquitectura esté clara)
# [tool.architectanalyst.layers]
# domain = []
# application = ["domain"]
# infrastructure = ["application", "domain"]
```

**Sobre la detección de capas**: Si tu proyecto no tiene una arquitectura en capas
explícita, dejá la sección `[layers]` comentada. Incorporarla prematuramente genera
falsos positivos que confunden al equipo.

### Paso 3: Establecer el ritmo de sprints

El valor de ArchitectAnalyst crece con el tiempo. Definí una cadencia desde el inicio:

```bash
# Al cierre de cada sprint
architectanalyst src/ --sprint-id sprint-XX
```

**Estrategia de adopción:**

| Sprint | Acción |
|--------|--------|
| Baseline | Primera corrida, identificar ciclos y módulos problemáticos |
| 1-2 | Correr con `--sprint-id`, observar sin actuar — construir histórico |
| 3-4 | Revisar tendencias en equipo (¿algo empeora sprint a sprint?) |
| 5-6 | Resolver ciclos de dependencias si existen (siempre CRITICAL) |
| 7-8 | Activar configuración de capas si la arquitectura lo justifica |
| 9+ | Monitorear D y I en los módulos del núcleo del negocio |

### Paso 4: Integrar al calendario del equipo

ArchitectAnalyst no va en el pre-commit ni en el PR review — su lugar es el **cierre de
sprint**. Incorporarlo como un paso en la retrospectiva técnica:

```bash
#!/bin/bash
# scripts/fin-de-sprint.sh

SPRINT_ID="${1:-sprint-$(date +%Y-%m)}"

echo "Ejecutando análisis arquitectónico del sprint $SPRINT_ID..."
architectanalyst src/ \
    --sprint-id "$SPRINT_ID" \
    --format json \
    > "reports/arquitectura-$SPRINT_ID.json"

echo "Análisis completado. Reporte en reports/arquitectura-$SPRINT_ID.json"
```

O en GitHub Actions como job programado (sin bloquear nada):

```yaml
# .github/workflows/architecture-audit.yml
name: Architecture Audit

on:
  workflow_dispatch:        # Manual al cerrar cada sprint
  schedule:
    - cron: '0 9 * * MON' # Alternativa: cada lunes a las 9hs

jobs:
  architect-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - name: Análisis arquitectónico
        run: |
          architectanalyst src/ \
            --sprint-id "$(date +%Y-W%V)" \
            --format json > architecture-report.json
      - uses: actions/upload-artifact@v4
        with:
          name: architecture-report
          path: architecture-report.json
        # exit code siempre 0 — el job nunca falla por este análisis
```

### Nota sobre el histórico

El historial de análisis se guarda en `.quality_control/architecture.db` (SQLite).
Decidir si versionarlo o no según las necesidades del equipo:

```gitignore
# Opción A: no versionar (histórico solo en la máquina local / CI)
.quality_control/

# Opción B: versionar el histórico (tendencias visibles para todo el equipo)
# No agregar nada al .gitignore
```

---

## Escenario B: Proyecto Nuevo

Acá la ventaja es enorme: **cada sprint tendrá histórico desde el primero**.
Las tendencias van a reflejar la evolución real de la arquitectura desde el inicio.

### Paso 1: Configuración estricta desde el inicio

Definí la arquitectura en capas **antes de escribir el primer módulo**:

```toml
[tool.architectanalyst]
max_instability = 0.8
max_distance_warning = 0.3
max_distance_critical = 0.5

db_path = ".quality_control/architecture.db"

exclude_patterns = [
    "__pycache__",
    ".venv",
    "tests",
    "dist",
    "build",
]

# Capas: declarar la arquitectura desde el día uno
[tool.architectanalyst.layers]
domain = []                               # domain no importa nada interno
application = ["domain"]                  # application puede importar domain
infrastructure = ["application", "domain"] # infrastructure puede importar ambas
```

### Paso 2: Verificar que el proyecto base pasa limpio

Antes del primer sprint real, corré ArchitectAnalyst sobre el estado inicial:

```bash
architectanalyst src/ --sprint-id sprint-00
# Debe mostrar 0 ciclos, 0 violaciones de capas
```

Si el scaffolding inicial ya genera violaciones de capas, revisá la configuración de
capas antes de continuar.

### Paso 3: Incorporar al cierre de cada sprint desde el inicio

```bash
# Al cerrar el sprint 1
architectanalyst src/ --sprint-id sprint-01
# Output: tendencias "—" (primer análisis)

# Al cerrar el sprint 2
architectanalyst src/ --sprint-id sprint-02
# Output: primeras tendencias ↑↓= comparando con sprint-01
```

Versionar el histórico para que todo el equipo pueda ver la evolución:

```bash
# Agregar al flujo de cierre de sprint
git add .quality_control/architecture.db
git commit -m "chore: snapshot arquitectura sprint-02"
```

### Paso 4: Revisión arquitectónica en la retrospectiva

Al cierre de cada sprint, revisar en equipo:

```bash
# Ver el estado actual con tendencias
architectanalyst src/ --sprint-id sprint-XX

# Exportar para compartir o archivar
architectanalyst src/ --sprint-id sprint-XX --format json > reports/sprint-XX.json
```

Preguntas a responder en cada revisión:
- ¿Hay nuevos ciclos de dependencias?
- ¿Los módulos del dominio mantienen I bajo?
- ¿La D de los módulos críticos mejoró, empeoró o se mantiene?
- ¿Algún módulo cruzó a la Zone of Pain (D > 0.5)?

---

## Referencia de Configuración

Todas las opciones disponibles en `[tool.architectanalyst]`:

```toml
[tool.architectanalyst]
# --- Métricas de Martin ---
max_instability = 0.8          # I > 0.8 → WARNING
max_distance_warning = 0.3     # D > 0.3 → WARNING
max_distance_critical = 0.5    # D > 0.5 → CRITICAL

# --- Persistencia ---
db_path = ".quality_control/architecture.db"

# --- Exclusiones ---
exclude_patterns = [
    "__pycache__",
    ".venv",
    "migrations",
    "tests",
    "dist",
    "build",
]

# --- IA (opt-in — desactivada por defecto) ---
[tool.architectanalyst.ai]
enabled = false

# --- Arquitectura en capas (opcional) ---
[tool.architectanalyst.layers]
domain = []
application = ["domain"]
infrastructure = ["application", "domain"]
```

### Comparación de perfiles

| | Proyecto existente | Proyecto nuevo |
|---|---|---|
| **Umbrales iniciales** | Defaults — foco en exclusiones | Defaults + capas desde el inicio |
| **Ciclos de dependencias** | Siempre CRITICAL — resolver antes de monitorear tendencias | Siempre CRITICAL |
| **Capas** | Activar cuando la arquitectura esté clara | Declarar antes del primer sprint |
| **Histórico** | Empieza en el primer análisis | Empieza en el sprint 0 |
| **Integración** | Script manual o workflow programado | Cierre de cada sprint |
| **Estrategia** | Construir histórico, luego interpretar tendencias | Tendencias visibles desde sprint 2 |

---

*Para más detalles: [Guía de Usuario Completa](architectanalyst.md)*
