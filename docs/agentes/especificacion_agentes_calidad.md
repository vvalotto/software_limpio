# ESPECIFICACIÓN DE AGENTES DE CONTROL DE CALIDAD
**Sistema de Control de Calidad en Tres Niveles**

Versión 1.3 - Marzo 2026

---

## ÍNDICE

1. [Visión General](#visión-general)
2. [Modelo de Distribución e Integración](#modelo-de-distribución-e-integración)
3. [Estructura de Configuración](#estructura-de-configuración)
4. [Agente de Código - "CodeGuard"](#agente-de-código---codeguard)
5. [Agente de Diseño - "DesignReviewer"](#agente-de-diseño---designreviewer)
6. [Agente de Arquitectura - "ArchitectAnalyst"](#agente-de-arquitectura---architectanalyst)
7. [Infraestructura Técnica](#infraestructura-técnica)
8. [Roadmap de Implementación](#roadmap-de-implementación)

---

## VISIÓN GENERAL

### Principios de Diseño

1. **Separación de responsabilidades**: Cada agente opera en su contexto específico
2. **No intrusividad**: Los controles no deben paralizar el desarrollo
3. **Progresividad**: De advertencias ligeras a análisis profundos
4. **Accionabilidad**: Todo reporte debe tener sugerencias concretas
5. **Educación**: Los agentes enseñan mientras controlan
6. **Modularidad y Cohesión**: Cada verificación es un componente autocontenido (Febrero 2026)

### Arquitectura del Sistema

```
Pre-commit (segundos)     Review (minutos)        Sprint-end (horas)
     ↓                          ↓                         ↓
  CodeGuard    ──────→   DesignReviewer   ──────→   ArchitectAnalyst
     │                          │                         │
  ADVERTIR                   BLOQUEAR                  ANALIZAR
     │                          │                         │
  CLI Output + JSON     CLI Output + JSON      CLI Output + JSON + Trends
```

### Arquitectura Interna Modular (Febrero 2026)

**Decisión arquitectónica:** Sistema modular con orquestación contextual

Cada agente implementa una **arquitectura modular** donde cada verificación/análisis/métrica es un componente independiente que decide cuándo debe ejecutarse según el contexto.

```
┌─────────────────────────────────────────────────────────┐
│                     AGENTE                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────┐            │
│  │         Orchestrator                   │            │
│  │  - Auto-discovery de verificables     │            │
│  │  - Selección contextual               │            │
│  │  - Presupuesto de tiempo              │            │
│  │  - Priorización                       │            │
│  └──────────┬─────────────────────────────┘            │
│             │                                           │
│             ├─→ Verifiable 1 (Check/Analyzer/Metric)  │
│             ├─→ Verifiable 2                          │
│             ├─→ Verifiable 3                          │
│             └─→ ...                                    │
│                                                         │
│  Cada verificable:                                     │
│  - name: str                                           │
│  - category: str                                       │
│  - estimated_duration: float                           │
│  - priority: int (1=alta, 10=baja)                    │
│  - should_run(context) -> bool                        │
│  - execute(file_path) -> results                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Características clave:**

1. **Modularidad**: Cada verificación es un componente independiente en su propio archivo
2. **Orquestación**: El orquestador decide qué ejecutar según:
   - Tipo de análisis (pre-commit, PR-review, full, sprint-end)
   - Presupuesto de tiempo (< 5s en pre-commit)
   - Prioridades y duración estimada
   - Contexto del archivo (nuevo, modificado, excluido)
   - Configuración habilitada
3. **Extensibilidad**: Agregar nueva verificación = crear clase + exportar (auto-discovery)
4. **Decisiones contextuales**: Cada verificable puede decidir si debe ejecutarse
5. **Preparado para IA**: El orquestador puede usar IA para selección inteligente

**Ejemplo de decisión contextual:**

```
Contexto: Pre-commit (time_budget=5s)
Archivo: src/utils.py (modificado)

Orquestador selecciona:
✓ PEP8Check        (0.5s, priority=2) → Ejecutar
✓ SecurityCheck    (1.5s, priority=1) → Ejecutar
✓ UnusedImports    (1.0s, priority=3) → Ejecutar
✗ PylintCheck      (2.0s, priority=4) → Omitir (sin presupuesto)
✗ TypesCheck       (2.0s, priority=6) → Omitir (baja prioridad)

Total: 3.0s de 5.0s disponibles
```

**Referencia:** Ver `docs/agentes/arquitectura_modular.md` para detalles completos.

### Estrategia de Bloqueo

| Agente | Bloquea | Advierte | Uso de IA | Tiempo |
|--------|---------|----------|-----------|--------|
| CodeGuard | NO | SÍ | Opcional (explicaciones) | < 5s |
| DesignReviewer | SÍ (crítico) | SÍ | Opcional (pendiente v0.4.0) | 2-5 min |
| ArchitectAnalyst | NO | SÍ | Opcional (pendiente v0.4.0) | 10-30 min |

---

## MODELO DE DISTRIBUCIÓN E INTEGRACIÓN

### Distribución del Framework

**Quality Agents** se distribuye como paquete Python instalable con soporte para múltiples formas de integración.

#### Instalación

```bash
# Instalación desde PyPI (recomendado)
pip install quality-agents

# Instalación desde repositorio
pip install git+https://github.com/vvalotto/software_limpio.git

# Instalación en modo desarrollo
git clone https://github.com/vvalotto/software_limpio.git
cd software_limpio
pip install -e ".[dev]"
```

#### Comandos Disponibles

Después de la instalación, tres comandos CLI están disponibles:

```bash
codeguard .                    # Verificación rápida pre-commit
designreviewer                 # Análisis profundo de diseño
architectanalyst               # Análisis estratégico de arquitectura
```

### Modelos de Integración

El framework soporta **4 modelos de integración** para máxima flexibilidad:

#### 1. Uso Directo desde Terminal

```bash
# Ejecutar manualmente cuando se necesite
codeguard .
codeguard src/ --config custom.toml
codeguard --format json .
```

**Ideal para:** Desarrollo local, verificación ad-hoc, debugging

#### 2. Framework pre-commit (Recomendado)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.1.0
    hooks:
      - id: codeguard
        name: CodeGuard Quality Check
        args: [--config=pyproject.toml]

      - id: designreviewer
        name: Design Review
        stages: [manual]  # Solo cuando se solicite explícitamente
```

**Instalación:**
```bash
pip install pre-commit
pre-commit install
```

**Ideal para:** Equipos profesionales, proyectos con múltiples herramientas de calidad

#### 3. Hook Git Manual

```bash
# En el proyecto destino
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
codeguard
exit 0  # Nunca bloquear
EOF

chmod +x .git/hooks/pre-commit
```

**Ideal para:** Proyectos simples, control total del hook

#### 4. GitHub Actions / CI/CD

```yaml
# .github/workflows/quality.yml
name: Quality Check

on:
  pull_request:
    branches: [main, develop]

jobs:
  codeguard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install quality-agents
        run: pip install quality-agents

      - name: Run CodeGuard
        run: codeguard .

  design-review:
    if: contains(github.event.pull_request.labels.*.name, 'design-review')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4

      - name: Install quality-agents
        run: pip install quality-agents

      - name: Run DesignReviewer
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: designreviewer

      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: design-review-report
          path: reports/design/
```

**Ideal para:** Proyectos open source, equipos distribuidos, verificación en PR

### Tabla Comparativa

| Modelo | Ejecución | Automatización | Flexibilidad | Complejidad |
|--------|-----------|----------------|--------------|-------------|
| **Directo** | Manual | Baja | Alta | Muy baja |
| **pre-commit** | Automática | Alta | Media | Baja |
| **Hook manual** | Automática | Media | Alta | Media |
| **CI/CD** | En la nube | Alta | Baja | Media-Alta |

---

## ESTRUCTURA DE CONFIGURACIÓN

### Configuración Moderna: pyproject.toml

**Quality Agents** sigue el estándar PEP 518 y usa `pyproject.toml` como archivo principal de configuración.

#### Ejemplo Completo

```toml
# pyproject.toml

[tool.codeguard]
# Umbrales
min_pylint_score = 8.0
max_cyclomatic_complexity = 10
max_line_length = 100
max_function_lines = 20

# Verificaciones habilitadas
check_pep8 = true
check_pylint = true
check_security = true
check_complexity = true
check_types = true
check_imports = true

# IA opcional para explicaciones
[tool.codeguard.ai]
enabled = false  # Opt-in (requiere ANTHROPIC_API_KEY)
explain_errors = true
suggest_fixes = true
max_tokens = 500

# Exclusiones
exclude_patterns = [
    "*.pyc",
    "__pycache__",
    ".venv",
    "venv",
    "migrations",
]

[tool.designreviewer]
# Umbrales de bloqueo
[tool.designreviewer.blocking_thresholds]
class_size = 200
wmc = 20
cc_per_class = 30
cbo = 5
dit = 5
nop = 1
duplicated_lines = 5.0
coverage = 70.0

# Umbrales de advertencia
[tool.designreviewer.warning_thresholds]
lcom = 1.0
mi = 20
fan_out = 7

# IA (siempre activa)
[tool.designreviewer.ai]
enabled = true
model = "claude-sonnet-4"
include_examples = true
include_effort_estimate = true

[tool.architectanalyst]
# Métricas de Martin
[tool.architectanalyst.thresholds]
distance_main_sequence = 0.2
tech_debt_ratio = 5.0
avg_cc = 5
duplicated_lines = 3.0
coverage = 80.0

# Análisis de tendencias
[tool.architectanalyst.trends]
history_sprints = 6
show_projections = true
projection_sprints = 3

# IA predictiva
[tool.architectanalyst.ai]
enabled = true
model = "claude-sonnet-4"
deep_dive = true
predictive_insights = true
```

### Configuración Legacy: Archivos YAML

Para compatibilidad con proyectos que no usan `pyproject.toml`, se soporta configuración via archivos YAML:

```yaml
# .codeguard.yml (en la raíz del proyecto)
min_pylint_score: 8.0
max_cyclomatic_complexity: 10
check_pep8: true
check_security: true

ai:
  enabled: false
  explain_errors: true
```

### Orden de Búsqueda de Configuración

Los agentes buscan configuración en este orden:

1. **pyproject.toml** (prioridad) → `[tool.codeguard]`
2. `.codeguard.yml` (fallback) → raíz del proyecto
3. **Defaults internos** → si no se encuentra ninguna config

Este orden permite:
- Proyectos modernos: usar `pyproject.toml` centralizado
- Proyectos legacy: mantener archivos `.yml` separados
- Proyectos sin config: funcionan con defaults razonables

---

## AGENTE DE CÓDIGO - "CodeGuard"

### 1.1 Propósito

Validación rápida de calidad básica de código antes de cada commit. **NO bloquea** el commit, solo advierte al desarrollador de problemas potenciales.

### 1.2 Momento de Activación

- **Trigger**: Pre-commit hook (Git)
- **Alcance**: Solo archivos modificados en el commit actual
- **Tiempo máximo**: 5 segundos

### 1.3 Métricas Monitoreadas

| # | Métrica | Umbral | Severidad | Acción |
|---|---------|--------|-----------|--------|
| 1 | PEP8 Violations | 0 | WARN | Advertir + listar violaciones |
| 2 | Pylint Score | ≥ 7.0 | WARN | Advertir si < 7.0 |
| 3 | Unused Imports | 0 | WARN | Advertir + sugerir autoflake |
| 4 | Insecure Functions | 0 | **ERROR** | Advertir + ejemplo seguro |
| 5 | Hardcoded Secrets | 0 | **ERROR** | Advertir + sugerir variables de entorno |
| 6 | Bare Excepts | 0 | WARN | Advertir + ejemplo específico |
| 7 | Type Errors | 0 | WARN | Solo si .py tiene type hints |
| 8 | CC por función | ≤ 15 | INFO | Informar si > 15 (no bloquea) |

### 1.4 Herramientas Necesarias

```bash
# Core tools
flake8              # PEP8 + errores básicos
pylint              # Score global + unused imports
bandit              # Seguridad (insecure functions, secrets)
mypy                # Type checking (solo si hay hints)
radon               # CC rápido

# IA (opcional)
anthropic           # Claude API para explicaciones de errores

# Opcional
autoflake           # Auto-fix unused imports
black               # Auto-formatting (sugerencia)
```

### 1.4.1 IA Opcional para Explicaciones

**CodeGuard** puede usar IA (Claude) para explicar errores detectados y sugerir correcciones.

**Características:**
- **Opt-in**: Deshabilitado por default (requiere configuración explícita)
- **Condicional**: Solo se activa si hay errores detectados
- **Rápido**: Llamada a API agrega ~2 segundos solo cuando hay errores
- **Educativo**: Explica *por qué* el código tiene problemas y *cómo* arreglarlo

**Flujo de ejecución:**
```
1. Ejecutar linters (flake8, pylint, bandit, radon)  [~2s]
2. Si NO hay errores → Terminar                      [Total: ~2s]
3. Si hay errores AND config.ai.enabled = true:
   - Enviar errores a Claude API                     [+2s]
   - Recibir explicación + sugerencias
   - Agregar al output                               [Total: ~4s]
4. Si hay errores AND config.ai.enabled = false:
   - Mostrar errores sin explicación IA              [Total: ~2s]
```

**Ejemplo de salida con IA:**
```
❌ ERROR: Hardcoded secret detected (line 45)
   Code: api_key = "sk-1234567890"

   🤖 AI Explanation:
   Hardcoding secrets in source code is a critical security vulnerability.
   If this code is committed to version control, the API key becomes
   accessible to anyone with repository access, including in commit history.

   Recommended fix:
   1. Store the key in environment variables
   2. Load it using: api_key = os.getenv('API_KEY')
   3. Add .env to .gitignore
   4. Document required env vars in README

   Example:
   ```python
   import os
   from dotenv import load_dotenv

   load_dotenv()
   api_key = os.getenv('API_KEY')
   if not api_key:
       raise ValueError("API_KEY environment variable not set")
   ```
```

### 1.5 Formato de Salida

**Terminal CLI - Colores:**

```
🔍 CodeGuard - Quality Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Analyzing: src/utils/helper.py

✅ PASS: PEP8 compliance
✅ PASS: No unused imports
⚠️  WARN: Pylint score 6.8/10 (threshold: 7.0)
❌ ERROR: Hardcoded secret detected (line 45)
   → Use environment variables: os.getenv('API_KEY')
⚠️  WARN: Bare except found (line 78)
   → Specify exception type: except ValueError:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary: 2 errors, 2 warnings in 3.2s

⚠️  Commit allowed but review recommended
💡 Run 'codeguard --fix' to auto-correct some issues
```

### 1.6 Comportamiento

1. **No bloquea el commit** - el desarrollador puede proceder
2. **Registro en log local** - mantiene histórico de advertencias
3. **Sugerencias automáticas básicas**:
   - Comando para auto-fix (ej: `black`, `autoflake`)
   - Ejemplo de código correcto
   - Link a documentación si aplica

### 1.7 Configuración

**Archivo: `pyproject.toml` (recomendado)**

```toml
[tool.codeguard]
# Umbrales
min_pylint_score = 8.0
max_cyclomatic_complexity = 10
max_line_length = 100
max_function_lines = 20

# Verificaciones habilitadas
check_pep8 = true
check_pylint = true
check_security = true
check_complexity = true
check_types = true
check_imports = true

# IA opcional para explicaciones
[tool.codeguard.ai]
enabled = false  # Opt-in (requiere ANTHROPIC_API_KEY)
explain_errors = true
suggest_fixes = true
max_tokens = 500

# Exclusiones
exclude_patterns = [
    "*.pyc",
    "__pycache__",
    ".venv",
    "venv",
    "migrations",
]
```

**Configuración Legacy (fallback): `.codeguard.yml`**

```yaml
min_pylint_score: 8.0
max_cyclomatic_complexity: 10
check_pep8: true
check_security: true

ai:
  enabled: false
  explain_errors: true
  suggest_fixes: true
```

**Variables de entorno:**

```bash
# Requerido solo si ai.enabled = true
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 1.8 Integración Técnica

**Ver sección [Modelo de Distribución e Integración](#modelo-de-distribución-e-integración)** para detalles completos sobre los 4 modelos soportados:

1. Uso directo desde terminal
2. Framework pre-commit (recomendado)
3. Hook Git manual
4. GitHub Actions / CI/CD

**Recordatorios importantes:**
- CodeGuard **NUNCA bloquea** commits (exit code siempre 0)
- IA es **opt-in** y solo se activa con errores presentes
- Tiempo de ejecución: < 2s sin errores, ~4s con errores + IA habilitada

### 1.9 Arquitectura Interna Modular

**Decisión arquitectónica (Febrero 2026):** CodeGuard implementa un sistema modular de checks con orquestación contextual.

#### Componentes

**1. Clase Base: `Verifiable`**

Todos los checks heredan de esta clase base ubicada en `shared/verifiable.py`:

```python
class Verifiable(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del check."""

    @property
    def estimated_duration(self) -> float:
        """Duración estimada en segundos (para presupuesto)."""
        return 1.0

    @property
    def priority(self) -> int:
        """Prioridad de ejecución: 1=alta, 10=baja."""
        return 5

    def should_run(self, context: ExecutionContext) -> bool:
        """Decide si debe ejecutarse en este contexto."""
        return not context.is_excluded

    @abstractmethod
    def execute(self, file_path: Path) -> List[CheckResult]:
        """Ejecuta el check."""
```

**2. Checks Específicos (Modulares)**

Cada check es un módulo autocontenido en `codeguard/checks/`:

| Check | Archivo | Priority | Duration | Categoría |
|-------|---------|----------|----------|-----------|
| PEP8 | `pep8_check.py` | 2 (alta) | 0.5s | style |
| Security | `security_check.py` | 1 (máxima) | 1.5s | security |
| Unused Imports | `imports_check.py` | 3 (alta) | 1.0s | quality |
| Pylint | `pylint_check.py` | 4 (media) | 2.0s | quality |
| Complexity | `complexity_check.py` | 5 (media) | 1.0s | quality |
| Types | `types_check.py` | 6 (baja) | 2.0s | quality |

**3. Orquestador (`CheckOrchestrator`)**

Decide qué checks ejecutar según el contexto:

```python
class CheckOrchestrator:
    def select_checks(self, context: ExecutionContext) -> List[Verifiable]:
        """
        Selecciona checks según:
        - Tipo de análisis (pre-commit, PR-review, full)
        - Presupuesto de tiempo
        - Prioridades
        - Configuración
        """
```

**Estrategias de selección:**

| Análisis | Estrategia | Checks Ejecutados |
|----------|-----------|-------------------|
| `pre-commit` | Solo rápidos (<2s) + alta prioridad (≤3) | PEP8, Security, UnusedImports |
| `pr-review` | Todos los habilitados | Todos |
| `full` | Todos los habilitados | Todos |

#### Flujo de Ejecución

```
1. CodeGuard.run(files, analysis_type="pre-commit")
2. Para cada archivo:
   a. Crear ExecutionContext:
      - file_path, analysis_type
      - time_budget (5s para pre-commit)
      - config, is_excluded, ai_enabled
   b. orchestrator.select_checks(context)
      - Filtrar por should_run()
      - Aplicar presupuesto de tiempo
      - Ordenar por prioridad
   c. Ejecutar checks seleccionados
   d. Agregar resultados
3. Retornar CheckResult list
```

#### Ejemplo de Decisión Contextual

**Escenario:** Pre-commit de `src/utils.py`

```python
context = ExecutionContext(
    file_path=Path("src/utils.py"),
    analysis_type="pre-commit",
    time_budget=5.0,
    config=config,
    is_excluded=False
)

# Orquestador evalúa:
# ✓ PEP8Check: should_run()=True, priority=2, duration=0.5s → EJECUTAR
# ✓ SecurityCheck: should_run()=True, priority=1, duration=1.5s → EJECUTAR
# ✓ UnusedImports: should_run()=True, priority=3, duration=1.0s → EJECUTAR
# ✗ PylintCheck: should_run()=True, priority=4, duration=2.0s → OMITIR (sin presupuesto)
# ✗ TypesCheck: should_run()=False (no type hints) → OMITIR

# Checks ejecutados: 3 (total 3.0s de 5.0s disponibles)
```

#### Ventajas de esta Arquitectura

| Aspecto | Beneficio |
|---------|-----------|
| **Mantenibilidad** | Agregar check = crear archivo nuevo, no modificar existente |
| **Testabilidad** | Cada check se prueba en aislamiento |
| **Flexibilidad** | Decisiones contextuales (tipo análisis, tiempo, archivo) |
| **Rendimiento** | Solo ejecuta checks relevantes según presupuesto |
| **Extensibilidad** | Auto-discovery permite agregar checks sin cambiar core |

#### Agregar Nuevo Check

Para agregar un nuevo check:

1. Crear `codeguard/checks/mi_check.py`:
```python
class MiCheck(Verifiable):
    @property
    def name(self) -> str:
        return "MiCheck"

    @property
    def priority(self) -> int:
        return 3

    def should_run(self, context) -> bool:
        return context.file_path.suffix == ".py"

    def execute(self, file_path) -> List[CheckResult]:
        # Implementación...
        return results
```

2. Exportar en `checks/__init__.py`:
```python
from .mi_check import MiCheck
__all__ = [..., "MiCheck"]
```

3. ✅ Listo - El orquestador lo descubre automáticamente

**Referencia:** Ver `src/quality_agents/codeguard/PLAN_IMPLEMENTACION.md` para plan de implementación completo.

---

## AGENTE DE DISEÑO - "DesignReviewer"

### 2.1 Propósito

Análisis profundo de calidad de diseño a nivel clase/módulo en momentos de review planificado. **SÍ bloquea** si hay violaciones críticas. La integración con IA es opcional y está pendiente para v0.4.0.

### 2.2 Momento de Activación

- **Trigger**: Manual o GitHub Actions en PR marcado con label "design-review"
- **Alcance**: Módulos/clases modificados + dependencias directas
- **Frecuencia**: Semanal o antes de merge importante
- **Tiempo esperado**: 2-5 minutos

### 2.3 Métricas Monitoreadas

| # | Métrica | Umbral | Severidad | Analyzer |
|---|---------|--------|-----------|----------|
| 1 | CBO (Coupling Between Objects) | ≤ 5 | **CRITICAL** | `CBOAnalyzer` |
| 2 | Fan-Out | ≤ 7 | WARNING | `FanOutAnalyzer` |
| 3 | Circular Imports | 0 | **CRITICAL** | `CircularImportsAnalyzer` |
| 4 | LCOM (Lack of Cohesion) | ≤ 1 | WARNING | `LCOMAnalyzer` |
| 5 | WMC (Weighted Methods per Class) | ≤ 20 | **CRITICAL** | `WMCAnalyzer` |
| 6 | DIT (Depth of Inheritance Tree) | ≤ 5 | **CRITICAL** | `DITAnalyzer` |
| 7 | NOP (Number of Parents) | ≤ 1 | **CRITICAL** | `NOPAnalyzer` |
| 8 | God Object | N clases > umbral | **CRITICAL** | `GodObjectAnalyzer` |
| 9 | Long Method | métodos > umbral | WARNING | `LongMethodAnalyzer` |
| 10 | Long Parameter List | parámetros > umbral | WARNING | `LongParameterListAnalyzer` |
| 11 | Feature Envy | métodos afectados | WARNING | `FeatureEnvyAnalyzer` |
| 12 | Data Clumps | grupos detectados | WARNING | `DataClumpsAnalyzer` |

### 2.4 Herramientas Utilizadas

```bash
# Análisis estático (ya incluidas en quality-agents)
radon               # CC, MI, Halstead
pylint              # Métricas OO (WMC, DIT, NOP, Fan-Out)
ast                 # Análisis AST propio (LCOM, CBO, code smells)
```

### 2.5 Formato de Salida

**CLI (Rich) + JSON:**

```
designreviewer src/

🔬 DesignReviewer - Análisis Profundo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚫 BLOCKING ISSUES (2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┌─────────────────────────────────────────────────────────────┐
│ CRITICAL  CBO: 8 (umbral: 5)                                │
│ Archivo: src/services/payment_processor.py                  │
│ Clase PaymentProcessor acoplada a 8 clases                  │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ CRITICAL  CircularImports detectados                        │
│ Ciclo: services.payment → models.user → services.payment    │
└─────────────────────────────────────────────────────────────┘

⚠️  Advertencias
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┌─────────────────────────────────────────────────────────────┐
│ Checker   │ Módulo                          │ Valor │ Umbral│
├───────────┼─────────────────────────────────┼───────┼───────┤
│ LCOM      │ src/models/user.py              │  1.3  │  1.0  │
│ LongMethod│ src/utils/validator.py:45       │ 65 LOC│  50   │
└─────────────────────────────────────────────────────────────┘

❌ REVISIÓN BLOQUEADA — Corregir issues CRITICAL antes del merge
   Exit code: 1
```

**Salida JSON** (`designreviewer --format json`):
```json
{
  "should_block": true,
  "violations": 2,
  "warnings": 2,
  "results": [
    {
      "analyzer": "CBOAnalyzer",
      "severity": "critical",
      "module": "src/services/payment_processor.py",
      "message": "CBO: 8 clases acopladas (umbral: 5)"
    }
  ]
}
```

### 2.6 Comportamiento

1. **Bloquea si hay issues CRITICAL** — el merge no puede proceder (exit code 1)
2. **Solo advierte si hay WARNING** — no bloquea (exit code 0)
3. **Salida formateada** con Rich en consola: sección BLOCKING separada de Advertencias
4. **Salida JSON** disponible con `--format json` para integración CI/CD (campo `should_block`)
5. **IA**: no implementada en v0.3.0 — pendiente para v0.4.0 como funcionalidad opt-in

### 2.7 Configuración

**Archivo: `pyproject.toml`** (sección `[tool.designreviewer]`)

```toml
[tool.designreviewer]
# Umbrales de acoplamiento
max_cbo = 5             # CBO > 5 → CRITICAL
max_fan_out = 7         # Fan-Out > 7 → WARNING

# Umbrales de cohesión y herencia
max_lcom = 1.0          # LCOM > 1.0 → WARNING
max_wmc = 20            # WMC > 20 → CRITICAL
max_dit = 5             # DIT > 5 → CRITICAL
max_nop = 1             # NOP > 1 → CRITICAL

# Code Smells
max_method_lines = 50   # Líneas por método → WARNING
max_parameters = 5      # Parámetros por función → WARNING

# Exclusiones
exclude = ["tests/", "migrations/", "__pycache__/"]

# IA (pendiente v0.4.0)
[tool.designreviewer.ai]
enabled = false
```

### 2.8 Integración con IA (pendiente v0.4.0)

La integración con IA es opt-in y está planificada para v0.4.0. Cuando esté implementada, Claude analizará las métricas problemáticas y sugerirá planes de refactorización específicos.

La configuración será:

```toml
[tool.designreviewer.ai]
enabled = true            # opt-in explícito
model = "claude-sonnet-4-6"
```

### 2.9 Arquitectura Interna Modular

**Decisión arquitectónica (Febrero 2026):** DesignReviewer implementa un sistema modular de analyzers con orquestación contextual.

#### Componentes

**1. Clase Base: `Verifiable`** (heredada de `shared/verifiable.py`)

Todos los analyzers heredan de la misma clase base que CodeGuard.

**2. Analyzers Específicos (Modulares)**

Cada analyzer es un módulo autocontenido en `designreviewer/analyzers/`:

| Analyzer | Archivo | Priority | Duration | Métrica |
|----------|---------|----------|----------|---------|
| LCOM | `lcom_analyzer.py` | 1 (máxima) | 3-5s | Cohesión |
| CBO | `cbo_analyzer.py` | 1 (máxima) | 2-4s | Acoplamiento |
| MI | `mi_analyzer.py` | 2 (alta) | 4-6s | Mantenibilidad |
| WMC | `wmc_analyzer.py` | 3 (alta) | 2-3s | Complejidad ponderada |

**3. Orquestador (`AnalyzerOrchestrator`)**

Decide qué analyzers ejecutar según el tipo de cambio:

| Tipo de Cambio | Analyzers Ejecutados |
|----------------|---------------------|
| **Refactoring** | LCOM + CBO (cohesión y acoplamiento) |
| **Feature nueva** | MI + WMC (mantenibilidad y complejidad) |
| **PR-review completo** | Todos los analyzers |

#### Decisión Contextual Inteligente

A diferencia de CodeGuard (presupuesto de tiempo), DesignReviewer usa **tipo de cambio** para seleccionar analyzers:

```python
context = ExecutionContext(
    analysis_type="refactoring",  # Detectado por diff
    files_changed=["src/models/user.py"],
    config=config
)

# Orquestador selecciona:
# ✓ LCOMAnalyzer → Ejecutar (verifica cohesión post-refactoring)
# ✓ CBOAnalyzer → Ejecutar (verifica acoplamiento)
# ✗ MIAnalyzer → Omitir (no crítico para refactoring)
```

#### IA en Analyzers

Cada analyzer puede usar IA para:
- **Explicar** por qué la métrica está fuera de umbral
- **Sugerir** refactorización específica
- **Mostrar** código de ejemplo mejorado

**Referencia:** Ver `src/quality_agents/designreviewer/` para la implementación completa.

---

## AGENTE DE ARQUITECTURA - "ArchitectAnalyst"

### 3.1 Propósito

Análisis estratégico de la arquitectura del sistema al finalizar sprints o hitos importantes. **NO bloquea** — genera reportes de tendencias y recomendaciones. La integración con IA es opcional y está pendiente para v0.4.0.

### 3.2 Momento de Activación

- **Trigger**: Manual, fin de sprint, o milestone de GitHub
- **Alcance**: Sistema completo
- **Frecuencia**: Quincenal o mensual
- **Tiempo esperado**: 10-30 minutos

### 3.3 Métricas Monitoreadas

| # | Métrica | Umbral | Categoría | Trend | Analyzer |
|---|---------|--------|-----------|-------|----------|
| 1 | Ca (Afferent Coupling) | — informativo | Martin | ↑↓= | `CouplingAnalyzer` |
| 2 | Ce (Efferent Coupling) | — informativo | Martin | ↑↓= | `CouplingAnalyzer` |
| 3 | I (Instability) | > 0.8 → WARNING | Martin | ↑↓= | `InstabilityAnalyzer` |
| 4 | A (Abstractness) | — informativo | Martin | ↑↓= | `AbstractnessAnalyzer` |
| 5 | D (Distance from Main Seq.) | > 0.3 → WARNING, > 0.5 → CRITICAL | Martin | ↑↓= | `DistanceAnalyzer` |
| 6 | Dependency Cycles | 0 → CRITICAL | Deps | ↑↓= | `DependencyCyclesAnalyzer` |
| 7 | Layer Violations | 0 → CRITICAL | Arch | ↑↓= | `LayerViolationsAnalyzer` |

**Leyenda trends:** ↑ Degradando · ↓ Mejorando · = Estable · — Sin histórico

### 3.4 Herramientas Utilizadas

```bash
# Análisis estático (incluidas en quality-agents)
ast                 # Análisis de imports y clases (propio)
sqlite3             # Persistencia de snapshots (stdlib)

# Pendiente v0.4.0 (opt-in)
anthropic-api       # Claude para análisis estratégico
```

### 3.5 Formato de Salida

**CLI (Rich) + JSON:**

```
architectanalyst src/ --sprint-id sprint-12

🏛️  ArchitectAnalyst — Análisis Estratégico
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Sprint: sprint-12
📊 Comparando con snapshot anterior

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Issues CRITICAL (1)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┌─────────────────────────────────────────────────────────────┐
│ CRITICAL ↑  LayerViolations: 2 violaciones detectadas       │
│ services.payment → models.database (import directo)         │
│ domain.entities → infrastructure.email                      │
└─────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Métricas de Martin (por módulo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┌─────────────────────┬──────┬──────┬──────┬──────┬───────┬──────┐
│ Módulo              │  Ca  │  Ce  │   I  │   A  │   D   │Trend │
├─────────────────────┼──────┼──────┼──────┼──────┼───────┼──────┤
│ domain/entities.py  │  8   │  0   │ 0.00 │ 1.00 │ 0.00  │  =   │
│ services/payment.py │  2   │  5   │ 0.71 │ 0.20 │ 0.09  │  ↑   │
│ infrastructure/db.py│  4   │  3   │ 0.43 │ 0.00 │ 0.57  │ WARN │
└─────────────────────┴──────┴──────┴──────┴──────┴───────┴──────┘

⚠️  infrastructure/db.py: D=0.57 (Zone of Pain) — umbral crítico: 0.5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Exit code: 0 (no bloquea — análisis informativo)
```

**Salida JSON** (`architectanalyst --format json`):
```json
{
  "sprint_id": "sprint-12",
  "snapshot_id": 5,
  "violations": 1,
  "warnings": 2,
  "results": [
    {
      "analyzer": "LayerViolationsAnalyzer",
      "severity": "critical",
      "metric": "LayerViolations",
      "value": 2,
      "trend": "degrading",
      "message": "2 violaciones de capas detectadas"
    }
  ]
}
```

### 3.6 Comportamiento

1. **NO bloquea desarrollo** — siempre exit code 0, es informativo y estratégico
2. **Guarda snapshot** en SQLite (`.quality_control/architecture.db`) al finalizar cada análisis
3. **Calcula tendencias** comparando con el snapshot anterior (↑ degradando / ↓ mejorando / = estable)
4. **Salida Rich** en consola con tabla de métricas por módulo y tendencias
5. **Salida JSON** disponible con `--format json` para integración CI/CD
6. **IA**: no implementada en v0.3.0 — pendiente para v0.4.0 como funcionalidad opt-in

### 3.7 Configuración

**Archivo: `pyproject.toml`** (sección `[tool.architectanalyst]`)

```toml
[tool.architectanalyst]
# Umbrales métricas de Martin
max_instability = 0.8          # I > 0.8 → WARNING
max_distance_warning = 0.3     # D > 0.3 → WARNING
max_distance_critical = 0.5    # D > 0.5 → CRITICAL

# Persistencia
db_path = ".quality_control/architecture.db"

# Exclusiones
exclude = ["__pycache__", ".venv", "migrations", "tests/", "dist/", "build/"]

# Arquitectura en capas (para LayerViolationsAnalyzer)
[tool.architectanalyst.layers]
domain = []
application = ["domain"]
infrastructure = ["application", "domain"]

# IA (pendiente v0.4.0)
[tool.architectanalyst.ai]
enabled = false
```

### 3.8 Integración con IA (pendiente v0.4.0)

La integración con IA es opt-in y está planificada para v0.4.0. Cuando esté implementada, Claude recibirá las métricas del sprint actual más el histórico de snapshots y generará análisis estratégico con tendencias y recomendaciones.

La configuración será:

```toml
[tool.architectanalyst.ai]
enabled = true            # opt-in explícito
model = "claude-sonnet-4-6"
```

### 3.9 Arquitectura Interna Modular

**Decisión arquitectónica (Febrero 2026):** ArchitectAnalyst implementa un sistema modular de metrics con orquestación contextual.

#### Componentes

**1. Clase Base: `Verifiable`** (heredada de `shared/verifiable.py`)

Todos los metrics heredan de la misma clase base que CodeGuard y DesignReviewer.

**2. Metrics Específicas (Modulares)**

Cada métrica es un módulo autocontenido en `architectanalyst/metrics/`:

| Metric | Archivo | Priority | Duration | Aspecto |
|--------|---------|----------|----------|---------|
| Martin Metrics | `martin_metrics.py` | 1 (máxima) | 5-8s | I, A, D (Main Sequence) |
| Stability | `stability_metrics.py` | 1 (máxima) | 4-6s | Ca, Ce, estabilidad |
| Cycles | `cycles_analyzer.py` | 2 (alta) | 6-10s | Ciclos de dependencias |
| Layer Violations | `layer_violations.py` | 3 (alta) | 3-5s | Violaciones arquitectónicas |

**3. Orquestador (`MetricsOrchestrator`)**

Decide qué métricas ejecutar según el tipo de análisis:

| Tipo de Análisis | Metrics Ejecutadas |
|------------------|-------------------|
| **Sprint-end** | Todas las métricas + snapshot en BD |
| **On-demand** | Métricas específicas según solicitud |
| **Trend analysis** | Comparación con snapshots históricos |

#### Persistencia con Snapshots

ArchitectAnalyst usa **SQLite** para almacenar snapshots de métricas (vía `SnapshotStore`):

```python
# Tablas en .quality_control/architecture.db
# snapshots(id, timestamp, sprint_id, project_path)
# results(id, snapshot_id, analyzer_name, metric_name,
#         module_path, value, threshold, severity, message)

# TrendCalculator compara el snapshot actual con el anterior
# y asigna MetricTrend.IMPROVING | STABLE | DEGRADING a cada resultado
```

#### Decisión Contextual

ArchitectAnalyst ejecuta **todas** las métricas en sprint-end, pero puede ejecutar subsets on-demand:

```python
context = ExecutionContext(
    analysis_type="on-demand",
    requested_metrics=["martin", "cycles"],  # Usuario solicita métricas específicas
    config=config
)

# Orquestador selecciona:
# ✓ MartinMetrics → Ejecutar
# ✓ CyclesAnalyzer → Ejecutar
# ✗ StabilityMetrics → Omitir (no solicitado)
# ✗ LayerViolations → Omitir (no solicitado)
```

**Referencia:** Ver `src/quality_agents/architectanalyst/` para la implementación completa.

---

## INFRAESTRUCTURA TÉCNICA

### 4.1 Stack Tecnológico

```yaml
Core:
  language: Python 3.11+
  package_manager: pip + venv

Analysis Tools (implementados):
  static_analysis:
    - flake8     # CodeGuard
    - pylint     # CodeGuard + DesignReviewer
    - bandit     # CodeGuard
    - mypy       # CodeGuard
  metrics:
    - radon      # Complejidad ciclomática, MI
    - ast        # Análisis propio: LCOM, CBO, code smells, Martin Metrics
  persistence:
    - sqlite3    # ArchitectAnalyst — snapshots históricos (stdlib)

CLI / Output:
  cli: click
  console: rich
  config: tomllib (3.11+) / tomli (3.10-)

AI (pendiente v0.4.0 — opt-in):
  provider: Anthropic
  model: claude-sonnet-4-6
  api: anthropic-sdk

CI/CD:
  git_hooks: pre-commit framework
  github_actions: pendiente
```

### 4.2 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                   Quality Control System                │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌──────────────────┐
│   CodeGuard   │   │DesignReviewer │   │ArchitectAnalyst  │
│   (Pre-commit)│   │  (On-demand)  │   │  (Sprint-end)    │
└───────┬───────┘   └───────┬───────┘   └────────┬─────────┘
        │                   │                    │
        └───────────────────┼────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌──────────────────┐
│   Analyzers   │   │  Formatters   │   │  SnapshotStore   │
│  (Verifiable) │   │  (Rich+JSON)  │   │   (SQLite)       │
└───────────────┘   └───────────────┘   └──────────────────┘
        │                   │                    │
        └───────────────────┼────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  Orchestrator │
                    │ + TrendCalc   │
                    └───────────────┘
```

### 4.3 Estructura de Directorios

```
project_root/
├── .quality_control/
│   └── architecture.db         # ArchitectAnalyst — snapshots SQLite
│
├── .git/
│   └── hooks/
│       └── pre-commit          # CodeGuard
│
├── pyproject.toml              # Configuración de los 3 agentes
│   # [tool.codeguard]
│   # [tool.designreviewer]
│   # [tool.architectanalyst]
│
└── src/quality_agents/         # Implementación del paquete
    ├── shared/
    │   ├── verifiable.py       # Clase base Verifiable + ExecutionContext
    │   ├── config.py           # QualityConfig
    │   └── reporting.py        # Generación de reportes
    ├── codeguard/
    │   ├── agent.py            # CLI + main()
    │   ├── orchestrator.py     # Selección contextual de checks
    │   └── checks/             # PEP8, Pylint, Security, Complexity, Type, Import
    ├── designreviewer/
    │   ├── agent.py            # CLI + main()
    │   ├── orchestrator.py     # Selección contextual de analyzers
    │   └── analyzers/          # CBO, FanOut, Circular, LCOM, WMC, DIT, NOP, code smells
    └── architectanalyst/
        ├── agent.py            # CLI + main()
        ├── orchestrator.py     # Ejecución de métricas
        ├── snapshots.py        # SnapshotStore (SQLite)
        ├── trends.py           # TrendCalculator
        ├── formatter.py        # Rich + JSON output
        └── metrics/            # CouplingAnalyzer, Instability, Abstractness, Distance,
                                # DependencyCycles, LayerViolations
```

### 4.4 Base de Datos de Histórico (ArchitectAnalyst)

**SQLite Schema** (`.quality_control/architecture.db`):

```sql
-- Un registro por ejecución de architectanalyst
CREATE TABLE snapshots (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp    TEXT    NOT NULL,
    sprint_id    TEXT,
    project_path TEXT    NOT NULL DEFAULT ''
);

-- Un registro por cada ArchitectureResult del análisis
CREATE TABLE results (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id   INTEGER NOT NULL,
    analyzer_name TEXT    NOT NULL,
    metric_name   TEXT    NOT NULL,
    module_path   TEXT    NOT NULL,
    value         REAL    NOT NULL,
    threshold     REAL,
    severity      TEXT    NOT NULL,  -- 'info' | 'warning' | 'critical'
    message       TEXT    NOT NULL,
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
);
```

---

## ROADMAP DE IMPLEMENTACIÓN

### Fase 1: MVP - CodeGuard ✅ (v0.1.0 — Febrero 2026)

**Objetivo:** Agente básico funcionando en pre-commit

- [x] Setup de proyecto y estructura modular (Verifiable + Orchestrator)
- [x] 6 checks: PEP8, Pylint, Security (bandit), Complexity (radon), Type (mypy), Import
- [x] CLI con Rich + JSON output
- [x] Configuración via `pyproject.toml` ([tool.codeguard])
- [x] Hook de pre-commit (siempre exit code 0 — solo advierte)
- [x] Tests unitarios e integración (~160 tests)

**Entregable:** `quality-agents v0.1.0` publicado en GitHub Releases

---

### Fase 2: DesignReviewer ✅ (v0.2.0 — Febrero 2026)

**Objetivo:** Análisis profundo de diseño a nivel clase/módulo

- [x] 12 analyzers: CBO, FanOut, CircularImports, LCOM, WMC, DIT, NOP, GodObject, LongMethod, LongParameterList, FeatureEnvy, DataClumps
- [x] CLI con Rich + JSON output, exit code 1 si hay CRITICAL
- [x] Configuración via `pyproject.toml` ([tool.designreviewer])
- [x] Tests unitarios e integración (~160 tests)

**Entregable:** `quality-agents v0.2.0` publicado en GitHub Releases

---

### Fase 3: ArchitectAnalyst ✅ (v0.3.0 — Marzo 2026)

**Objetivo:** Análisis estratégico de arquitectura con tendencias históricas

- [x] 7 métricas de Martin: Ca, Ce, I, A, D + DependencyCycles + LayerViolations
- [x] SnapshotStore (SQLite) para persistencia histórica entre sprints
- [x] TrendCalculator para comparación sprint-actual vs anterior (↑↓=)
- [x] CLI con Rich + JSON output, siempre exit code 0 (informativo)
- [x] Configuración via `pyproject.toml` ([tool.architectanalyst])
- [x] Tests unitarios e integración + E2E (~200 tests)

**Entregable:** `quality-agents v0.3.0` publicado en GitHub Releases

---

### Fase 4: Integración IA opt-in (v0.4.0 — pendiente)

**Objetivo:** Agregar análisis IA opcional a los 3 agentes

- [ ] CodeGuard: explicaciones IA para warnings (opt-in)
- [ ] DesignReviewer: sugerencias de refactorización IA (opt-in)
- [ ] ArchitectAnalyst: análisis estratégico IA con histórico (opt-in)
- [ ] Publicación en PyPI (`pip install quality-agents`)
- [ ] GitHub Actions CI/CD

**Entregable:** `quality-agents v0.4.0`

---

## CONSIDERACIONES FINALES

### Para Proyectos Personales

1. **Empezar simple**: Solo CodeGuard inicialmente
2. **Iterar basado en valor real**: No implementar todo de golpe
3. **Métricas selectivas**: Usar solo las que realmente importan
4. **IA como asistente**: No como dependencia crítica

### Para Estudiantes

1. **Educación gradual**:
   - Semestre 1: Solo CodeGuard (conceptos básicos)
   - Semestre 2: + DesignReviewer (diseño OO)
   - Semestre 3: + ArchitectAnalyst (arquitectura)

2. **Gamificación**:
   - Badges por mejoras de métricas
   - Leaderboard de calidad entre equipos
   - Challenges mensuales

3. **Aprendizaje visible**:
   - Los reportes explican POR QUÉ cada métrica importa
   - Links a material educativo
   - Ejemplos de código antes/después

### Métricas de Éxito del Sistema

**Para validar que el sistema funciona:**

1. **Adopción**:
   - % de commits que pasan CodeGuard sin warnings
   - % de PRs que requieren re-review por DesignReviewer

2. **Impacto en calidad**:
   - Evolución de technical debt ratio
   - Evolución de bugs en producción
   - Tiempo de onboarding de nuevos devs

3. **Eficiencia**:
   - Tiempo promedio de CodeGuard (debe ser < 5s)
   - Tiempo de DesignReviewer (debe ser < 5min)
   - Tasa de falsos positivos (debe ser < 10%)

4. **Educación** (para estudiantes):
   - Mejora en scores de código a lo largo del semestre
   - Comprensión de principios de diseño (encuestas)
   - Autonomía en refactorización

---

**Versión:** 1.3
**Fecha:** Marzo 2026
**Autor:** Sistema de Control de Calidad - ISSE
**Licencia:** MIT (para uso académico y personal)
