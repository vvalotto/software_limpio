# Guía de Uso - DesignReviewer

> Agente de análisis de calidad de diseño para Pull Requests

**DesignReviewer** analiza la calidad de diseño de los archivos Python de un changeset y **puede bloquear el merge** si detecta violaciones críticas. A diferencia de CodeGuard (que solo advierte), DesignReviewer actúa como guardián de la calidad de diseño en el proceso de revisión de PRs.

---

## Índice

1. [Cuándo Usar DesignReviewer](#cuándo-usar-designreviewer)
2. [Instalación](#instalación)
3. [Uso Básico](#uso-básico)
4. [Métricas Analizadas](#métricas-analizadas)
5. [Interpretación de Resultados](#interpretación-de-resultados)
6. [Configuración](#configuración)
7. [Salida JSON](#salida-json)
8. [Integración con CI/CD](#integración-con-cicd)
9. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Cuándo Usar DesignReviewer

| Herramienta | Momento | Duración | Acción |
|-------------|---------|----------|--------|
| **CodeGuard** | Pre-commit | < 5s | Advierte, no bloquea |
| **DesignReviewer** | PR Review | 2-5 min | **Bloquea si hay CRITICAL** |
| ArchitectAnalyst | Fin de sprint | 10-30 min | Analiza tendencias |

Usá DesignReviewer cuando quieras garantizar que el código que se mergea no introduce problemas de diseño: clases demasiado acopladas, herencia excesiva, baja cohesión, o code smells que violan principios SOLID.

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
designreviewer --help
```

---

## Uso Básico

### Analizar un directorio

```bash
designreviewer src/
```

### Analizar un archivo específico

```bash
designreviewer src/quality_agents/servicio.py
```

### Salida en JSON (para CI/CD)

```bash
designreviewer src/ --format json
designreviewer src/ --format json > report.json
```

### Con configuración personalizada

```bash
designreviewer src/ --config configs/designreviewer.yml
```

### Sin sugerencias de IA

```bash
designreviewer src/ --no-ai
```

### Exit codes

| Código | Significado |
|--------|-------------|
| `0` | Sin violaciones CRITICAL (puede haber warnings) |
| `1` | Al menos una violación CRITICAL — **bloquea el merge** |

---

## Métricas Analizadas

DesignReviewer ejecuta **12 analyzers** sobre cada archivo Python del changeset.

### Acoplamiento

#### CBO — Coupling Between Objects
Cuenta cuántas clases distintas usa cada clase. Alto acoplamiento = alta fragilidad.

| Umbral | Severidad |
|--------|-----------|
| CBO > 5 | CRITICAL |

```python
# ❌ CBO = 8 — usa demasiadas clases externas
class ServicioFacturacion:
    def __init__(self):
        self.cliente = ClienteRepo()
        self.producto = ProductoRepo()
        self.impuesto = CalculadorImpuesto()
        self.email = EmailService()
        self.pdf = GeneradorPDF()
        self.auditoria = AuditoriaService()
        self.notificacion = NotificacionService()
        self.cache = CacheService()
```

#### Fan-Out
Cuenta los módulos importados por archivo. Muchos imports = muchas dependencias.

| Umbral | Severidad |
|--------|-----------|
| Fan-Out > 7 | WARNING |

#### Importaciones Circulares
Detecta ciclos de dependencias entre módulos (`A` importa `B` que importa `A`).

| Umbral | Severidad |
|--------|-----------|
| Ciclo detectado | CRITICAL |

---

### Cohesión y Herencia

#### LCOM — Lack of Cohesion of Methods
Mide cuántos grupos de métodos no comparten atributos. LCOM > 1 indica que la clase debería dividirse.

| Umbral | Severidad |
|--------|-----------|
| LCOM > 1 | WARNING |

```python
# ❌ LCOM = 3 — tres grupos de métodos sin relación
class ClaseInconexa:
    def __init__(self):
        self.nombre = ""    # solo lo usan los métodos del grupo 1
        self.saldo = 0.0   # solo lo usan los métodos del grupo 2
        self.telefono = "" # solo lo usan los métodos del grupo 3
```

#### WMC — Weighted Methods per Class
Suma la complejidad ciclomática de todos los métodos de la clase (via radon). Una clase con WMC alto hace demasiado.

| Umbral | Severidad |
|--------|-----------|
| WMC > 20 | CRITICAL |

#### DIT — Depth of Inheritance Tree
Profundidad del árbol de herencia. Herencia profunda = código difícil de entender y modificar.

| Umbral | Severidad |
|--------|-----------|
| DIT > 5 | CRITICAL |

#### NOP — Number of Parents
Número de clases padre directas (herencia múltiple). Más de una clase padre = señal de alerta.

| Umbral | Severidad |
|--------|-----------|
| NOP > 1 | CRITICAL |

---

### Code Smells y Principios SOLID

#### God Object (SRP)
Clase con demasiados métodos — viola el Principio de Responsabilidad Única.

| Umbral | Severidad |
|--------|-----------|
| > 10 métodos | WARNING |
| > 20 métodos | CRITICAL |

#### Long Method (SRP)
Método con demasiadas líneas — hace varias cosas a la vez.

| Umbral | Severidad |
|--------|-----------|
| > 20 líneas | WARNING |
| > 40 líneas | CRITICAL |

#### Long Parameter List (ISP)
Función o método con demasiados parámetros — señal de que agrupa conceptos distintos.

| Umbral | Severidad |
|--------|-----------|
| > 4 parámetros | WARNING |
| > 7 parámetros | CRITICAL |

#### Feature Envy (SRP/DIP)
Método que accede más a datos de otra clase que a los propios — debería estar en esa otra clase.

| Umbral | Severidad |
|--------|-----------|
| Detectado | WARNING |

#### Data Clumps (SRP)
Grupos de parámetros que siempre aparecen juntos — candidatos a convertirse en una clase propia.

| Umbral | Severidad |
|--------|-----------|
| Detectado | WARNING |

---

## Interpretación de Resultados

### Salida normal (modo text)

```
╭──────────────────────────────────────────────────────────╮
│  🔍  DesignReviewer - Análisis de Calidad de Diseño      │
╰──────────────────────────────────────────────────────────╯

Archivos analizados:   7
Analyzers ejecutados:  12
Tiempo de ejecución:   0.07s
Resultados totales:    3

╭──────────────────────────────────────────────────────────╮
│                  🚫 BLOCKING ISSUES (1)                  │
│  WMCAnalyzer │ GestorUniversal │ WMC=23 (umbral: 20)    │
╰──────────────────────────────────────────────────────────╯

             Advertencias de Diseño (2)
  LCOMAnalyzer       │ Calculator │ LCOM=2 (umbral: 1)
  LongMethodAnalyzer │ servicio   │ 35 líneas (umbral: 20)

╭──────────────────────────────────────────────────────────╮
│  ⏱  Deuda Técnica                                        │
│    Blocking issues: 0.9h                                 │
│    Total del changeset: 3.2h                             │
╰──────────────────────────────────────────────────────────╯
```

### Paneles de la salida

| Panel | Color | Significado |
|-------|-------|-------------|
| 🚫 BLOCKING ISSUES | Rojo | Violaciones CRITICAL — el merge debe bloquearse |
| Advertencias de Diseño | Amarillo | Violaciones WARNING — recomendable corregir |
| Informativos | Azul | Observaciones — considerar en el futuro |
| ⏱ Deuda Técnica | Cyan | Estimación de horas de refactoring necesarias |

### Columnas de las tablas

| Columna | Descripción |
|---------|-------------|
| **Analyzer** | Nombre del analyzer que detectó el problema |
| **Clase / Módulo** | Clase o archivo donde se detectó |
| **Problema** | Descripción del problema |
| **Valor** | Métrica medida |
| **Umbral** | Límite configurado |
| **Esfuerzo** | Horas estimadas de refactoring |

---

## Configuración

En tu `pyproject.toml`:

```toml
[tool.designreviewer]
# Acoplamiento
max_cbo = 5              # Coupling Between Objects
max_fan_out = 7          # Fan-Out por módulo

# Cohesión y herencia
max_lcom = 1             # Lack of Cohesion of Methods
max_wmc = 20             # Weighted Methods per Class
max_dit = 5              # Depth of Inheritance Tree
max_nop = 1              # Number of Parents

# Code Smells
max_methods_per_class = 10     # God Object (warning)
max_methods_critical = 20      # God Object (critical)
max_method_lines = 20          # Long Method (warning)
max_method_lines_critical = 40 # Long Method (critical)
max_parameters = 4             # Long Parameter List (warning)
max_parameters_critical = 7    # Long Parameter List (critical)
```

### Valores por defecto

Si no configurás `[tool.designreviewer]`, se usan los umbrales mostrados en la tabla de métricas. Son los valores de la literatura de ingeniería de software.

---

## Salida JSON

Con `--format json`, el output es un JSON estructurado apto para CI/CD y herramientas de análisis:

```bash
designreviewer src/ --format json | python -m json.tool
```

### Estructura

```json
{
  "summary": {
    "total_files": 7,
    "analyzers_executed": 12,
    "elapsed_seconds": 0.07,
    "timestamp": "2026-02-21T10:30:00",
    "total_issues": 3,
    "blocking_issues": 1,
    "warnings": 2,
    "infos": 0,
    "should_block": true,
    "estimated_effort_hours": {
      "blocking": 0.9,
      "total": 3.2
    }
  },
  "results": [
    {
      "analyzer": "WMCAnalyzer",
      "severity": "critical",
      "message": "Clase 'GestorUniversal' tiene WMC=23 (umbral: 20)",
      "file": "src/gestor.py",
      "class": "GestorUniversal",
      "current_value": 23,
      "threshold": 20,
      "estimated_effort_hours": 0.9,
      "solid_principle": null,
      "smell_type": null,
      "suggestion": null
    }
  ],
  "by_severity": {
    "critical": [...],
    "warning": [...],
    "info": []
  }
}
```

### Campo `should_block`

El campo `summary.should_block` es el indicador principal para CI/CD:
- `true` → hay al menos un CRITICAL → el merge debe bloquearse
- `false` → solo warnings o limpio → el merge puede proceder

---

## Integración con CI/CD

### GitHub Actions

```yaml
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
      - name: Instalar dependencias
        run: pip install -e ".[dev]"
      - name: Ejecutar DesignReviewer
        run: designreviewer src/ --format json > design_report.json
      - name: Verificar resultado
        run: |
          SHOULD_BLOCK=$(python -c "import json; d=json.load(open('design_report.json')); print(d['summary']['should_block'])")
          if [ "$SHOULD_BLOCK" = "True" ]; then
            echo "❌ DesignReviewer encontró violaciones CRITICAL"
            exit 1
          fi
      - name: Subir reporte
        uses: actions/upload-artifact@v4
        with:
          name: design-report
          path: design_report.json
```

### Script de pre-merge

```bash
#!/bin/bash
# pre-merge.sh — ejecutar antes de mergear un PR

set -e

echo "Ejecutando DesignReviewer..."
designreviewer src/

if [ $? -eq 1 ]; then
    echo "❌ Merge bloqueado: violaciones CRITICAL detectadas"
    exit 1
fi

echo "✅ DesignReviewer: sin violaciones críticas"
```

---

## Preguntas Frecuentes

### ¿Por qué bloquea con warnings en otros proyectos pero no aquí?

DesignReviewer solo bloquea (exit code 1) cuando hay violaciones **CRITICAL**. Las warnings son observaciones que recomendamos corregir pero no bloquean el merge.

### ¿Puedo ajustar los umbrales?

Sí, mediante `[tool.designreviewer]` en `pyproject.toml`. Los umbrales por defecto siguen la literatura de ingeniería de software, pero cada proyecto puede tener distintas necesidades.

### ¿Qué es `estimated_effort_hours`?

Es una estimación de horas de refactoring calculada por cada analyzer según la magnitud de la violación. Es orientativa — sirve para priorizar trabajo.

### ¿Analiza solo los archivos modificados en el PR?

En su configuración actual, analiza todos los archivos Python del PATH especificado. Para analizar solo el delta de un PR, pasá explícitamente los archivos modificados:

```bash
# Obtener archivos modificados en el PR
FILES=$(git diff --name-only origin/main...HEAD -- '*.py')
designreviewer $FILES
```

### ¿Funciona con herencia de clases de otras librerías?

Sí. DITAnalyzer y NOPAnalyzer usan AST puro y cuentan solo la herencia definida en el código analizado. No resuelve imports de librerías externas.

### ¿Qué pasa si un analyzer falla?

Si un analyzer lanza una excepción inesperada, el orquestador lo registra como INFO y continúa con los demás. No se interrumpe el análisis completo.

---

## Ver también

- [Guía de CodeGuard](codeguard.md) — análisis pre-commit
- [Especificación de Agentes](../agentes/especificacion_agentes_calidad.md) — diseño del sistema
- [Métricas de Diseño](../metricas/diseno.md) — catálogo completo de métricas
