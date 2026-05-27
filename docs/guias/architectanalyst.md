# Guía de Uso - ArchitectAnalyst

> Agente de análisis arquitectónico para fin de sprint

**ArchitectAnalyst** analiza la **salud arquitectónica del sistema completo** al finalizar un sprint. A diferencia de CodeGuard y DesignReviewer, **nunca bloquea** — es un agente informativo y estratégico. Su propósito es mostrar la evolución de la arquitectura entre sprints y detectar problemas estructurales antes de que se conviertan en deuda técnica crítica.

---

## Índice

1. [Cuándo Usar ArchitectAnalyst](#cuándo-usar-architectanalyst)
2. [Instalación](#instalación)
3. [Uso Básico](#uso-básico)
4. [Métricas Analizadas](#métricas-analizadas)
5. [Tendencias Históricas](#tendencias-históricas)
6. [Configuración](#configuración)
7. [Salida JSON](#salida-json)
8. [Integración en el Workflow](#integración-en-el-workflow)
9. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Cuándo Usar ArchitectAnalyst

| Herramienta | Momento | Duración | Acción |
|-------------|---------|----------|--------|
| **CodeGuard** | Pre-commit | < 5s | Advierte, no bloquea |
| **DesignReviewer** | PR Review | 2-5 min | **Bloquea si hay CRITICAL** |
| **ArchitectAnalyst** | Fin de sprint | 10-30 min | **Informa — exit code siempre 0** |

Usá ArchitectAnalyst al cerrar cada sprint para responder preguntas estratégicas:

- ¿La arquitectura se está volviendo más acoplada con el tiempo?
- ¿Hay ciclos de dependencias que antes no existían?
- ¿Los módulos del núcleo del negocio están en la posición correcta del Main Sequence?
- ¿Las capas definidas están siendo respetadas por todo el equipo?

---

## Instalación

```bash
# Clonar e instalar
git clone https://github.com/vvalotto/software_limpio.git
cd software_limpio
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Verificar
architectanalyst --help
```

---

## Uso Básico

### Analizar el proyecto completo

```bash
architectanalyst src/
```

### Analizar múltiples paquetes explícitamente (recomendado)

En proyectos con Clean Architecture donde los módulos fuente conviven con `.venv/`, `tests/` y herramientas de desarrollo en el mismo directorio raíz, es preferible pasar los paquetes explícitamente en lugar de apuntar al directorio raíz:

```bash
# Pasar uno o más paquetes/directorios
architectanalyst entidades servicios_dominio gestores_entidades configurador

# Equivalente a apuntar al src/ si la estructura lo permite
architectanalyst src/
```

El parent común de todos los paths se usa automáticamente como raíz del proyecto para cargar configuración y resolver nombres de módulos.

### Con identificador de sprint (recomendado)

```bash
architectanalyst src/ --sprint-id sprint-12
architectanalyst entidades servicios --sprint-id 2026-Q1
```

El `--sprint-id` se almacena junto con el snapshot y aparece en el output. Si no se provee, el snapshot usa el timestamp como identificador.

### Salida en JSON (para dashboards y CI)

```bash
architectanalyst src/ --format json
architectanalyst src/ --format json --sprint-id sprint-12 > arquitectura-sprint-12.json
```

### Con configuración personalizada

```bash
architectanalyst src/ --config pyproject.toml
architectanalyst src/ --config examples/configs/architectanalyst.yml
```

### Exit code

| Código | Significado |
|--------|-------------|
| `0` | **Siempre** — ArchitectAnalyst nunca bloquea |

ArchitectAnalyst es un agente de **observabilidad**, no de gatekeeping. Los problemas que detecta requieren decisiones de arquitectura que escapan a una validación automática de CI.

---

## Métricas Analizadas

ArchitectAnalyst ejecuta **9 métricas** (Métricas de Martin, análisis estructurales y calidad).

### Métricas de Martin

Las métricas de Robert C. Martin caracterizan la posición de cada paquete en el **Main Sequence** — la línea diagonal que representa el equilibrio ideal entre estabilidad y abstracción.

#### Ca — Afferent Coupling (Acoplamiento Aferente)

Cuántos módulos internos del proyecto **dependen de** este módulo. Alta Ca = módulo muy usado = cambiar este módulo tiene alto impacto.

| Umbral | Severidad |
|--------|-----------|
| Sin umbral | INFO — solo referencia |

```
# Ejemplo: módulo shared/config.py con Ca=8
# → muchos módulos dependen de él → estable, no modificar sin cuidado
```

#### Ce — Efferent Coupling (Acoplamiento Eferente)

Cuántos módulos internos del proyecto **importa** este módulo. Alta Ce = módulo con muchas dependencias = frágil, fácil de desestabilizar.

| Umbral | Severidad |
|--------|-----------|
| Sin umbral | INFO — solo referencia |

#### I — Instability (Inestabilidad)

`I = Ce / (Ca + Ce)` — valores entre 0 (muy estable) y 1 (muy inestable).

- **I = 0**: Nadie lo importa, importa a muchos → responsabilidad — **muy estable**
- **I = 1**: Muchos lo importan, no importa a nadie → perfectamente inestable — **muy frágil**

| Umbral | Severidad |
|--------|-----------|
| I > 0.8 | WARNING |

**Calibración por rol de módulo (`layer_roles`):** En arquitecturas CQRS, Event Sourcing o Hexagonal, algunos módulos tienen un comportamiento esperado que difiere del patrón general. Con `layer_roles` podés declarar el rol de módulos específicos para que el analyzer evalúe correctamente:

- `leaf`: módulo terminal — se advierte si tiene dependientes (Ca > 0 e I bajo), porque un leaf no debería ser dependido por otros.
- `stable`: módulo estable por diseño — se advierte si I es alto (comportamiento original).

```toml
[tool.architectanalyst.layer_roles]
"*/commands/*" = "leaf"    # módulos de comandos no deberían tener dependientes
"*/queries/*"  = "leaf"
"*/domain/*"   = "stable"  # domain debe ser estable
```

Los patrones usan sintaxis glob (`fnmatch`). El nombre del módulo se convierte a path (`.` → `/`) antes de comparar.

#### A — Abstractness (Abstracción)

`A = clases abstractas / total de clases` — qué fracción de las clases del módulo son abstractas o interfaces.

| Umbral | Severidad |
|--------|-----------|
| Sin umbral | INFO — solo referencia |

#### D — Distance from Main Sequence (Distancia)

`D = |A + I - 1|` — distancia al equilibrio ideal. Un paquete en la Main Sequence (`A + I ≈ 1`) es sano. Un paquete que se aleja cae en:

- **Zone of Pain** (D alto, A≈0, I≈0): paquete estable y concreto — rígido, difícil de cambiar
- **Zone of Uselessness** (D alto, A≈1, I≈1): paquete abstracto e inestable — interfaces sin usuarios estables

> **Nota:** D se calcula a nivel de **paquete**, no de módulo individual. La granularidad del paquete se controla con `analysis_depth` (default: 1 = primer componente del módulo). Con `depth=2`, `myapp.domain.model` → paquete `myapp.domain`, útil en arquitecturas hexagonales con namespace de aplicación.

| Umbral | Severidad |
|--------|-----------|
| D > 0.3 | WARNING |
| D > 0.5 | CRITICAL |

```
Main Sequence:

A
│ Zone of Uselessness
1│╲
 │  ╲  ← módulos ideales sobre esta diagonal
 │    ╲
0│______╲__
 0         1  I
        Zone of Pain
```

---

### Ciclos de Dependencias

Detecta ciclos en el grafo completo de imports del proyecto usando el **algoritmo de Tarjan** (Strongly Connected Components).

A diferencia de CircularImportsAnalyzer de DesignReviewer (que solo detecta ciclos directos A↔B), este analyzer detecta ciclos de cualquier longitud: A→B→C→A.

Los ciclos violan el **Acyclic Dependencies Principle (ADP)** de Robert C. Martin.

| Umbral | Severidad |
|--------|-----------|
| 1 o más ciclos | CRITICAL |

```python
# ❌ Ciclo A → B → C → A
# modulo_a.py
import modulo_b  # a depende de b

# modulo_b.py
import modulo_c  # b depende de c

# modulo_c.py
import modulo_a  # c depende de a → ¡ciclo!
```

---

### Violaciones de Capas

Detecta imports que violan las reglas de dependencia entre capas declaradas en la configuración. Se activa **solo si se configuran reglas de capas**.

| Umbral | Severidad |
|--------|-----------|
| 1 o más violaciones | CRITICAL |

Para activarlo, declarar las capas en `pyproject.toml`:

```toml
[tool.architectanalyst.layers]
domain = []                              # domain no puede importar nada interno
application = ["domain"]                 # application puede importar domain
infrastructure = ["application", "domain"]  # infrastructure puede importar ambas
```

Con esta configuración, un módulo en `domain/` que importe algo de `application/` será CRITICAL.

---

### Cohesión Relacional

#### H — Relational Cohesion (Cohesión Relacional)

`H = (R + 1) / N` — relación entre las relaciones internas de un paquete y el número de tipos (clases) que contiene.

- **R**: imports entre módulos del mismo paquete (relaciones internas)
- **N**: total de clases en el paquete

Un H bajo indica que las clases del paquete no se usan entre sí — probablemente deberían estar en paquetes distintos.

| Umbral | Severidad |
|--------|-----------|
| H < min_relational_cohesion (default: 1.5) | WARNING |

Rango esperado según Martin: **1.5 – 4.0**. Paquetes con menos de 2 clases se omiten (H no es significativo).

---

### God Package

Detecta paquetes con demasiada concentración — el análogo arquitectónico del God Object de DesignReviewer. Un God Package es un smell crítico porque atrae dependencias y responsabilidades, haciendo que cualquier cambio en él impacte a todo el sistema.

Se manifiesta de dos formas:

**Por tamaño:** demasiadas clases en un paquete (responsabilidades mezcladas)

| Umbral | Severidad |
|--------|-----------|
| n_clases > max_package_classes (default: 20) | WARNING |

**Por acoplamiento aferente:** Ca muy alto — casi todo el sistema depende de este paquete

| Umbral | Severidad |
|--------|-----------|
| Ca > max_package_ca (default: 10) | WARNING |

---

### Cobertura de Tests

Lee el archivo `coverage.json` generado por `pytest --cov --cov-report=json` y reporta el porcentaje de líneas cubiertas.

| Situación | Severidad |
|-----------|-----------|
| Archivo no encontrado | WARNING |
| Archivo inválido o ilegible | WARNING |
| Cobertura < min_coverage (default: 80%) | WARNING |
| Cobertura ≥ min_coverage | INFO |

Para generar el archivo de cobertura:

```bash
pytest --cov=src --cov-report=json
```

La ruta del archivo es configurable con `coverage_report_path` (default: `coverage.json`, relativo al project_path).

---

## Tendencias Históricas

Cada análisis se guarda automáticamente en una base de datos SQLite (`.quality_control/architecture.db`). A partir del **segundo análisis**, cada resultado incluye un indicador de tendencia:

| Símbolo | Significado |
|---------|-------------|
| `↓` | La métrica **mejoró** desde el análisis anterior |
| `=` | La métrica se mantuvo **estable** |
| `↑` | La métrica **empeoró** desde el análisis anterior |
| `—` | Sin histórico (primer análisis) |

### Flujo típico

```bash
# Sprint 11 - análisis inicial
architectanalyst src/ --sprint-id sprint-11
# Output: todas las tendencias muestran "—" (sin histórico)

# Sprint 12 - segundo análisis
architectanalyst src/ --sprint-id sprint-12
# Output: tendencias ↑↓= comparando con sprint-11
```

La base de datos se crea automáticamente en `.quality_control/architecture.db`. Agregarlo al `.gitignore` si no se quiere versionar el histórico.

---

## Configuración

ArchitectAnalyst se configura en `pyproject.toml`:

```toml
[tool.architectanalyst]
# Umbrales de Métricas de Martin
max_instability       = 0.8   # I > 0.8 → WARNING
max_distance_warning  = 0.3   # D > 0.3 → WARNING
max_distance_critical = 0.5   # D > 0.5 → CRITICAL

# Granularidad de paquete (aplica a DistanceAnalyzer y RelationalCohesionAnalyzer)
analysis_depth = 1   # 1 = primer componente (default), 2 = dos componentes (hexagonal)

# Cohesión Relacional
min_relational_cohesion = 1.5  # H < 1.5 → WARNING

# God Package
max_package_classes = 20   # n_clases > 20 → WARNING
max_package_ca      = 10   # Ca > 10 → WARNING

# Cobertura de tests
min_coverage         = 80.0          # cobertura < 80% → WARNING
coverage_report_path = "coverage.json"  # relativo al project_path

# Persistencia
db_path = ".quality_control/architecture.db"

# Exclusiones
exclude_patterns = [
    "__pycache__",
    ".venv",
    "venv",
    "migrations",
    "test_",
    "conftest",
    "dist",
    "build",
]

# Métricas habilitadas (todas activas por defecto)
[tool.architectanalyst.checks]
coupling            = true
abstractness        = true
instability         = true
distance            = true
dependency_cycles   = true
layer_violations    = true
relational_cohesion = true   # Cohesión relacional H
god_package         = true   # God Package por tamaño o Ca
coverage            = true   # Cobertura de tests

# IA (opt-in — desactivada por defecto)
[tool.architectanalyst.ai]
enabled    = false
max_tokens = 1500

# Roles de módulo para calibrar InstabilityAnalyzer (opcional, CQRS/ES/Hexagonal)
[tool.architectanalyst.layer_roles]
# "*/commands/*" = "leaf"    # módulos terminales
# "*/queries/*"  = "leaf"
# "*/domain/*"   = "stable"  # módulos estables

# Arquitectura en capas (opcional)
[tool.architectanalyst.layers]
# domain         = []
# application    = ["domain"]
# infrastructure = ["application", "domain"]
```

### Deshabilitar métricas específicas

```toml
[tool.architectanalyst.checks]
layer_violations    = false   # Si no se usan reglas de capas
god_package         = false   # Deshabilitar detección de God Package
coverage            = false   # Deshabilitar análisis de cobertura
relational_cohesion = false   # Deshabilitar cohesión relacional
```

### Umbrales por defecto

| Métrica | Umbral WARNING | Umbral CRITICAL | Fuente |
|---------|---------------|-----------------|--------|
| I (Instability) | > 0.8 | — | Cálculo (Ca, Ce) |
| D (Distance) | > 0.3 | > 0.5 | Cálculo (A, I) |
| H (Relational Cohesion) | < 1.5 | — | AST + grafo |
| God Package (clases) | > 20 clases | — | AST |
| God Package (Ca) | > 10 | — | Grafo |
| Cobertura | < 80% | — | coverage.json |
| Ciclos | — | ≥ 1 ciclo | AST + Tarjan |
| Violaciones de capas | — | ≥ 1 violación | AST + config |

---

## Salida JSON

La opción `--format json` produce un JSON bien estructurado ideal para dashboards e integración con herramientas externas:

```json
{
  "summary": {
    "sprint_id": "sprint-12",
    "total_files": 45,
    "metrics_executed": 9,
    "elapsed_seconds": 3.21,
    "timestamp": "2026-03-01T15:30:00.000Z",
    "total_results": 28,
    "critical_violations": 0,
    "warnings": 3,
    "infos": 25,
    "trend_available": true,
    "should_block": false
  },
  "results": [
    {
      "analyzer": "DistanceAnalyzer",
      "metric": "D",
      "severity": "warning",
      "message": "Distancia D=0.35 > 0.3 ...",
      "module": "quality_agents/codeguard/agent",
      "value": 0.35,
      "threshold": 0.3,
      "trend": "degrading",
      "trend_symbol": "↑"
    }
  ],
  "by_severity": {
    "critical": [],
    "warning": [...],
    "info": [...]
  }
}
```

**Campo `should_block`**: siempre `false` — ArchitectAnalyst nunca bloquea un proceso de CI/CD.

**Campo `trend_available`**: `true` si hay histórico de al menos un análisis anterior.

---

## Integración en el Workflow

### Script de cierre de sprint

```bash
#!/bin/bash
# scripts/fin-de-sprint.sh

SPRINT_ID="sprint-$(date +%Y-%m)"

echo "📊 Ejecutando análisis arquitectónico del sprint $SPRINT_ID..."
architectanalyst src/ \
    --sprint-id "$SPRINT_ID" \
    --format json \
    > "reports/arquitectura-$SPRINT_ID.json"

echo "✅ Análisis completado. Reporte en reports/arquitectura-$SPRINT_ID.json"
```

### En GitHub Actions (informativo, sin bloquear)

```yaml
# .github/workflows/architecture-audit.yml
name: Architecture Audit

on:
  workflow_dispatch:          # Manual (fin de sprint)
  schedule:
    - cron: '0 9 * * MON'   # Cada lunes a las 9hs

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
        # Siempre sube el reporte (exit code siempre 0)
```

---

## Preguntas Frecuentes

**¿Por qué exit code siempre 0?**

ArchitectAnalyst es un agente de observabilidad estratégica. Los problemas que detecta (módulo en Zone of Pain, ciclos entre módulos de test, etc.) requieren decisiones de diseño que no se pueden automatizar como un check binario. A diferencia de DesignReviewer, que bloquea merges puntuales, ArchitectAnalyst provee visión de la evolución del sistema.

**¿Qué es la "Zone of Pain"?**

Un paquete con A≈0 (sin abstracciones) e I≈0 (no depende de otros paquetes) tiene D=1.0 — máxima distancia del Main Sequence. Es concreto y estable: funciona, pero es difícil de modificar sin romper todo. Muchos paquetes de infraestructura caen aquí y está bien — el indicador advierte para que el equipo sea consciente.

> D se calcula a nivel de paquete. Un paquete con clases concretas que *sí depende* de otros paquetes (I > 0) o *sí es usado* (Ca > 0) puede tener D aceptable.

**¿Con qué frecuencia usar ArchitectAnalyst?**

Al menos una vez por sprint. En proyectos con mucha actividad, puede correrse semanalmente. Lo importante es la tendencia acumulada, no el valor puntual de cada sprint.

**¿Qué hago si aparecen ciclos de dependencias?**

Un ciclo de dependencias es siempre CRITICAL porque viola el ADP. La solución clásica es aplicar el Dependency Inversion Principle: introducir una interfaz abstracta en la capa más estable del ciclo para romperlo.

**¿Los archivos de test se analizan?**

No — el patrón `test_` está excluido por defecto en `exclude_patterns`. Los tests suelen tener alta instabilidad (I≈1) por diseño, lo que distorsionaría las métricas del código productivo. Los patrones se aplican sobre la **ruta relativa** al directorio analizado, así que un path absoluto que contenga `test_` no genera falsos positivos.

**¿Se detectan clases abstractas definidas con `metaclass=ABCMeta`?**

Sí. `AbstractnessAnalyzer` y `DistanceAnalyzer` detectan clases abstractas por tres criterios:
1. Heredan de `ABC`, `Protocol` o `ABCMeta`
2. Usan `metaclass=ABCMeta` (patrón Python 3.5+ para compatibilidad con versiones sin `ABC` como base)
3. Tienen al menos un método decorado con `@abstractmethod`

```python
# Todos estos patrones se detectan como abstractos:
class A(ABC): ...
class B(metaclass=ABCMeta): ...
class C:
    @abstractmethod
    def metodo(self): ...
```

**¿Cómo funciona la detección de capas?**

El analyzer busca el nombre de la capa como segmento del nombre de módulo dotted. Dado `[domain, application, infrastructure]`, el módulo `myapp.domain.entity` pertenece a la capa `domain`. Si ese módulo importa algo de `myapp.application`, se genera un CRITICAL.

**¿Qué pasa si el archivo `architecture.db` no existe?**

Se crea automáticamente en el primer análisis. El directorio `.quality_control/` también se crea si no existe.

**¿Qué es `analysis_depth` y cuándo usarlo?**

Controla la granularidad del paquete para DistanceAnalyzer y RelationalCohesionAnalyzer. Con el default (`depth=1`), `myapp.domain.model` → paquete `myapp`. Con `depth=2` → paquete `myapp.domain`. Usá `depth=2` en proyectos con arquitecturas hexagonales o Clean Architecture donde el primer componente del módulo es el namespace de la aplicación y el segundo es la capa real (`domain`, `application`, `infrastructure`).

**¿Para qué sirve `layer_roles`?**

Calibra la advertencia de InstabilityAnalyzer para módulos que tienen un comportamiento esperado distinto del patrón estándar. Ejemplo: en CQRS, los módulos de commands son "leaves" — no deberían tener dependientes. Sin `layer_roles`, InstabilityAnalyzer no advertiría si un leaf tiene Ca alto porque su I sería bajo (muchos dependientes = parece estable). Con `"*/commands/*" = "leaf"`, el analyzer advierte cuando un leaf tiene dependientes inesperados.

**¿Por qué CoverageAnalyzer advierte si no encuentra `coverage.json`?**

Porque la ausencia del archivo implica que los tests no se están corriendo con cobertura, lo cual es información valiosa. Generá el archivo con `pytest --cov=src --cov-report=json` antes de correr ArchitectAnalyst. Podés deshabilitar este check con `coverage = false` en `[tool.architectanalyst.checks]`.
