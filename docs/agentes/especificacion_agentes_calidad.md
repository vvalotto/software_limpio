# ESPECIFICACIÓN DE AGENTES DE CONTROL DE CALIDAD
**Sistema de Control de Calidad en Tres Niveles**

Versión 1.1 - Enero 2026

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
  CLI Output              HTML Report              Dashboard + Trends
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

**Referencia:** Ver `docs/agentes/decision_arquitectura_checks_modulares.md` para detalles completos.

### Estrategia de Bloqueo

| Agente | Bloquea | Advierte | Uso de IA | Tiempo |
|--------|---------|----------|-----------|--------|
| CodeGuard | NO | SÍ | Opcional (explicaciones) | < 5s |
| DesignReviewer | SÍ (crítico) | SÍ | Siempre (refactoring) | 2-5 min |
| ArchitectAnalyst | NO | SÍ | Siempre (predictivo) | 10-30 min |

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

Análisis profundo de calidad de diseño a nivel clase/módulo en momentos de review planificado. **SÍ bloquea** si hay violaciones críticas. Utiliza IA para sugerir refactorizaciones.

### 2.2 Momento de Activación

- **Trigger**: Manual o GitHub Actions en PR marcado con label "design-review"
- **Alcance**: Módulos/clases modificados + dependencias directas
- **Frecuencia**: Semanal o antes de merge importante
- **Tiempo esperado**: 2-5 minutos

### 2.3 Métricas Monitoreadas

| # | Métrica | Umbral | Severidad | Acción |
|---|---------|--------|-----------|--------|
| 1 | Average Class Size | ≤ 200 LOC | **BLOCK** | Bloquear + sugerir split |
| 2 | WMC | ≤ 20 | **BLOCK** | Bloquear + IA sugiere extractos |
| 3 | CC por clase | ≤ 30 | **BLOCK** | Bloquear + refactorizar |
| 4 | LCOM | ≤ 1 | WARN | Advertir + IA sugiere cohesión |
| 5 | CBO | ≤ 5 | **BLOCK** | Bloquear + IA sugiere desacople |
| 6 | Fan-Out | ≤ 7 | WARN | Advertir dependencies |
| 7 | DIT | ≤ 5 | **BLOCK** | Bloquear herencia profunda |
| 8 | NOP | ≤ 1 | **BLOCK** | Bloquear herencia múltiple |
| 9 | MI | > 20 | WARN | Advertir si < 20 |
| 10 | Tech Debt Ratio | < 5% | WARN | Advertir tendencia |
| 11 | Code Smells | 0 críticos | **BLOCK** | Bloquear + listar |
| 12 | Duplicated Lines | < 3% | **BLOCK** | Bloquear si > 5% |
| 13 | Duplicated Blocks | 0 | WARN | Advertir + mostrar |
| 14 | Line Coverage | > 80% | **BLOCK** | Bloquear si < 70% |
| 15 | Branch Coverage | > 75% | WARN | Advertir si < 70% |
| 16 | Bugs (SonarQube) | 0 | **BLOCK** | Bloquear + priorizar |
| 17 | Circular Imports | 0 | **BLOCK** | Bloquear diseño |
| 18 | README actualizado | Sí | WARN | Advertir si falta |

### 2.4 Herramientas Necesarias

```bash
# Análisis estático
radon               # CC, MI, Halstead
pylint              # Múltiples métricas OO
pydeps              # Dependencias y grafos
coverage.py         # Cobertura de tests
jscpd               # Detección de duplicación

# Plataforma integrada
sonarqube           # Dashboard completo (opcional pero recomendado)

# IA
anthropic-api       # Claude para sugerencias de refactoring
```

### 2.5 Formato de Salida

**HTML Report + CLI Summary:**

```
🔬 DesignReviewer - Deep Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Module: src/services/payment_processor.py

🚫 BLOCKING ISSUES (3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Class Size: 287 LOC (threshold: 200)
   📍 Class: PaymentProcessor (lines 45-332)
   💡 AI Suggestion:
      - Extract validation logic → PaymentValidator class
      - Extract formatting → PaymentFormatter class
      - Keep core processing in PaymentProcessor
   📄 See detailed refactoring plan in HTML report

2. CBO: 8 coupled classes (threshold: 5)
   📍 Class: PaymentProcessor
   🔗 Coupled to: Database, Logger, Validator, Formatter, 
                  EmailService, SMSService, PushNotifier, Analytics
   💡 AI Suggestion:
      - Introduce NotificationService facade
      - Use dependency injection for observability
   
3. Duplicated Code: 5.2% (threshold: 3%)
   📍 Duplicated blocks: 3
   🔍 Locations:
      - payment_processor.py:145-167 ↔️ refund_processor.py:89-111
      - payment_processor.py:201-215 ↔️ subscription_handler.py:67-81
   💡 AI Suggestion:
      - Extract common validation to shared module
      - Create TransactionValidator base class

⚠️  WARNINGS (2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. LCOM: 1.3 (threshold: 1.0)
   📍 Methods not sharing attributes detected
   💡 Consider splitting into cohesive classes

2. MI: 18.5 (threshold: 20)
   📍 Maintainability slightly below target

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Full report: design_review_20251228_143052.html
🤖 AI Analysis: design_suggestions_20251228_143052.md

❌ REVIEW BLOCKED - Fix blocking issues before merge
```

### 2.6 Comportamiento

1. **Bloquea si hay issues críticos** - el merge no puede proceder
2. **Genera reporte HTML completo** con visualizaciones:
   - Gráfico de dependencias
   - Mapa de calor de complejidad
   - Evolución de métricas (si hay histórico)
3. **IA genera sugerencias detalladas**:
   - Plan de refactorización paso a paso
   - Ejemplos de código antes/después
   - Estimación de esfuerzo
4. **Modo interactivo opcional**:
   - El desarrollador puede pedir excepciones justificadas
   - Se registra la justificación para auditoría

### 2.7 Configuración

**Archivo: `.designreviewer.yml`**

```yaml
enabled: true
run_on_pr_label: "design-review"
auto_run_weekly: true

blocking_thresholds:
  class_size: 200
  wmc: 20
  cc_per_class: 30
  cbo: 5
  dit: 5
  nop: 1
  duplicated_lines: 5.0
  coverage: 70.0
  bugs: 0
  circular_imports: 0
  code_smells_critical: 0

warning_thresholds:
  lcom: 1.0
  mi: 20
  fan_out: 7
  tech_debt_ratio: 5.0
  branch_coverage: 75.0

ai_suggestions:
  enabled: true
  model: "claude-sonnet-4"
  include_examples: true
  include_effort_estimate: true

reports:
  html: true
  html_path: "reports/design_reviews/"
  include_graphs: true
  include_history: true

exceptions:
  allow_justified: true
  require_approval: true  # Requiere aprobación de lead
```

### 2.8 Integración con IA

**Prompt Template para Claude:**

```python
REFACTORING_PROMPT = """
Analiza el siguiente código y las métricas de calidad detectadas:

**Código:**
```python
{code}
```

**Métricas problemáticas:**
- {metric_1}: {value_1} (umbral: {threshold_1})
- {metric_2}: {value_2} (umbral: {threshold_2})

**Contexto del proyecto:**
- Lenguaje: Python 3.11
- Paradigma: {paradigm}
- Restricciones: {constraints}

**Solicitud:**
1. Identifica los problemas de diseño específicos
2. Propón un plan de refactorización con pasos concretos
3. Muestra ejemplo de código refactorizado
4. Estima esfuerzo (horas) y riesgo (bajo/medio/alto)
5. Sugiere tests adicionales necesarios

**Formato de respuesta:**
Markdown estructurado con secciones claras.
"""
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

**Referencia:** Ver `src/quality_agents/designreviewer/` (implementación futura).

---

## AGENTE DE ARQUITECTURA - "ArchitectAnalyst"

### 3.1 Propósito

Análisis estratégico de la arquitectura del sistema al finalizar sprints o hitos importantes. **NO bloquea** pero genera reportes de tendencias y recomendaciones estratégicas con IA.

### 3.2 Momento de Activación

- **Trigger**: Manual, fin de sprint, o milestone de GitHub
- **Alcance**: Sistema completo
- **Frecuencia**: Quincenal o mensual
- **Tiempo esperado**: 10-30 minutos

### 3.3 Métricas Monitoreadas

| # | Métrica | Umbral | Categoría | Trend |
|---|---------|--------|-----------|-------|
| 1 | Ca (Afferent Coupling) | Contexto | Martin | ↗️↘️ |
| 2 | Ce (Efferent Coupling) | Contexto | Martin | ↗️↘️ |
| 3 | I (Instability) | Contexto | Martin | ↗️↘️ |
| 4 | A (Abstractness) | Contexto | Martin | ↗️↘️ |
| 5 | D (Distance) | ≈ 0 | Martin | ↗️↘️ |
| 6 | D' (Normalized Distance) | ≈ 0 | Martin | ↗️↘️ |
| 7 | Total Dependencies | ≤ 30 | Deps | ↗️↘️ |
| 8 | Direct Dependencies | ≤ 15 | Deps | ↗️↘️ |
| 9 | Outdated Dependencies | 0 | Deps | ↗️↘️ |
| 10 | Dependency Cycles | 0 | Deps | ❌ |
| 11 | Layer Violations | 0 | Clean Arch | ❌ |
| 12 | Inward Dependencies | 100% | Clean Arch | ✅ |
| 13 | Outward Dependencies | 0 | Clean Arch | ❌ |
| 14 | Domain Purity | 100% | Clean Arch | ✅ |
| 15 | Cyclic Dependencies (DSM) | 0 | DSM | ❌ |
| 16 | Layering Violations (DSM) | 0 | DSM | ❌ |
| 17 | Vulnerabilities | 0 | Security | ❌ |
| 18 | Security Rating | A | Security | ↗️↘️ |
| 19 | Dependency CVEs | 0 | Security | ❌ |
| 20 | Total Line Coverage | > 80% | Testing | ↗️↘️ |
| 21 | Tests Passed | 100% | Testing | ✅ |
| 22 | Average MI | > 20 | Quality | ↗️↘️ |
| 23 | Tech Debt Ratio | < 5% | Quality | ↗️↘️ |
| 24 | Average CC | ≤ 5 | Quality | ↗️↘️ |
| 25 | Total Duplicated Lines | < 3% | Quality | ↗️↘️ |

**Leyenda:**
- ↗️↘️ = Monitorear tendencia (subiendo/bajando)
- ❌ = Debe ser cero (crítico)
- ✅ = Debe ser 100% (crítico)

### 3.4 Herramientas Necesarias

```bash
# Análisis de dependencias
pydeps              # Grafos completos
import-linter       # Validación de reglas
pipdeptree          # Árbol de dependencias
safety              # CVEs
pip-audit           # Vulnerabilidades

# Análisis arquitectónico
radon               # Métricas agregadas
sonarqube           # Dashboard (recomendado)
wily                # Histórico de métricas

# IA
anthropic-api       # Claude para análisis estratégico
```

### 3.5 Formato de Salida

**Dashboard Web Interactivo + Markdown Report:**

```
🏛️ ArchitectAnalyst - Strategic Review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Sprint: S2025-W51 (Dec 16-27)
📊 Comparison: vs. Sprint S2025-W49

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 CRITICAL ISSUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Layer Violations: 2 (was 0)
   📍 services.payment → models.database (direct import)
   📍 domain.entities → infrastructure.email
   💡 AI Analysis:
      "Violation 1 breaks Clean Architecture. The service layer
       should not import from models directly. Create a repository
       interface in domain and implement in infrastructure."
   📋 Suggested Actions:
      1. Create PaymentRepository interface in domain/
      2. Implement in infrastructure/repositories/
      3. Inject via dependency injection
   ⏱️  Estimated effort: 4 hours
   🎯 Priority: HIGH

❌ Dependency CVEs: 1 (was 0)
   📦 requests==2.28.0 → CVE-2023-32681 (CVSS 7.5)
   💡 Fix: Upgrade to requests>=2.31.0
   ⏱️  Effort: 15 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 TRENDING METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Technical Debt Ratio
   Current: 6.2% ⬆️ +1.5% (threshold: 5%)
   Trend:   ─────────────╱
   [Chart showing 6-sprint trend]
   
   💡 AI Analysis:
      "Debt is accumulating in the payment module (35% of total).
       Root cause: Rushed features in last 2 sprints without
       refactoring time. Recommend dedicating 20% of next sprint
       to cleanup."

📊 Average CC
   Current: 5.8 ⬆️ +0.6 (threshold: 5)
   Worst modules:
   1. payment_processor.py: avg CC 8.2
   2. data_validator.py: avg CC 7.5
   3. report_generator.py: avg CC 6.9
   
   💡 Recommendation: Schedule refactoring spike

📊 Dependencies
   Total: 28 ⬆️ +3 (threshold: 30)
   Direct: 14 ⬆️ +2 (threshold: 15)
   ⚠️  Warning: Approaching limits
   
   New dependencies added:
   - pandas (needed)
   - requests-mock (test only, ok)
   - rich (console output, consider if essential)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 ARCHITECTURAL PATTERNS ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Clean Architecture Compliance: 92% (was 95%)
   - Domain purity: 100% ✅
   - Inward dependencies: 100% ✅
   - Outward dependencies: 2 ❌ (layer violations)

📊 Martin Metrics (Distance from Main Sequence)
   Package Analysis:
   
   domain/         D=0.05 ✅ (Excellent)
   services/       D=0.12 ✅ (Good)
   infrastructure/ D=0.28 ⚠️  (Review needed)
   api/            D=0.15 ✅ (Good)
   
   [Scatter plot of A vs I with packages plotted]
   
   💡 AI Analysis:
      "infrastructure package is in Zone of Pain (high concrete,
       high stability). This makes changes expensive. Consider:
       1. Extract interfaces to separate package
       2. Increase abstraction through adapters
       3. Review if all code here belongs in infrastructure"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔮 PREDICTIVE INSIGHTS (AI-POWERED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📉 Risk Assessment: MODERATE

1. Technical Debt Trajectory
   "At current growth rate (1.5%/sprint), debt will reach 10%
    in 3 sprints. Recommend debt reduction sprint before S2025-W55."

2. Dependency Bloat
   "Adding 2-3 direct dependencies per sprint is unsustainable.
    Total dependencies will exceed 30 in 1 sprint. Consider:
    - Dependency audit before adding new ones
    - Evaluate if existing libraries can cover new needs"

3. Complexity Hotspots
   "payment_processor.py is becoming a God Object:
    - 287 LOC (growing 15%/sprint)
    - CBO of 8 (was 5 two sprints ago)
    - Avg CC of 8.2 (was 5.5)
    
    Projected to become unmaintainable in 2-3 sprints if not
    addressed. High-priority refactoring needed."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ POSITIVE TRENDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Test Coverage: 84% ⬆️ +3% (Excellent improvement!)
✨ Duplicated Code: 2.1% ⬇️ -0.8% (Great work!)
✨ Security Rating: A (maintained)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 RECOMMENDED ACTIONS FOR NEXT SPRINT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Priority 1 (Critical):
□ Fix layer violations (2 issues)
□ Upgrade requests to fix CVE
□ Review infrastructure package architecture

Priority 2 (Important):
□ Refactor payment_processor.py (split into 3 classes)
□ Debt reduction: allocate 20% sprint capacity
□ Dependency audit before adding new ones

Priority 3 (Maintenance):
□ Continue improving test coverage target: 90%
□ Document architectural decisions (ADRs)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Full dashboard: architect_review_20251228.html
📈 Metrics history: metrics_trend_6sprints.html
🤖 AI Deep Dive: architecture_analysis_20251228.md
```

### 3.6 Comportamiento

1. **NO bloquea desarrollo** - es informativo y estratégico
2. **Dashboard web interactivo** con:
   - Gráficos de tendencias (últimos 6 sprints)
   - Visualización de arquitectura (grafos de dependencias)
   - Main Sequence plot (Martin metrics)
   - Hotspots de complejidad (heatmap)
3. **IA analiza patrones y predice**:
   - Proyección de métricas (2-3 sprints adelante)
   - Identificación de problemas emergentes
   - Recomendaciones estratégicas priorizadas
   - Estimación de esfuerzo de corrección
4. **Genera informe ejecutivo** para stakeholders:
   - Versión técnica detallada (Markdown)
   - Versión ejecutiva (PDF de 2 páginas)
   - Presentación de 5 slides (PPTX)

### 3.7 Configuración

**Archivo: `.architectanalyst.yml`**

```yaml
enabled: true
run_on_sprint_end: true
run_on_milestone: true
manual_trigger: true

schedule:
  frequency: "biweekly"  # weekly | biweekly | monthly
  day: "friday"
  time: "18:00"

analysis_scope:
  full_system: true
  include_tests: true
  include_docs: true

thresholds:
  # Martin Metrics
  distance_main_sequence: 0.2
  zone_of_pain_warning: 0.3
  
  # Dependencies
  total_dependencies: 30
  direct_dependencies: 15
  outdated_warning: 3
  
  # Clean Architecture
  layer_violations: 0
  domain_purity: 100
  
  # Security
  vulnerabilities: 0
  security_rating: "A"
  
  # Quality
  avg_mi: 20
  tech_debt_ratio: 5.0
  avg_cc: 5
  duplicated_lines: 3.0
  coverage: 80.0

trends:
  history_sprints: 6
  show_projections: true
  projection_sprints: 3
  alert_negative_trends: true

ai_analysis:
  enabled: true
  model: "claude-sonnet-4"
  deep_dive: true
  predictive_insights: true
  include_recommendations: true
  prioritize_actions: true
  estimate_effort: true

reports:
  dashboard_html: true
  markdown_report: true
  executive_pdf: true
  presentation_pptx: true
  output_dir: "reports/architecture/"
  
notifications:
  email: true
  slack: true
  recipients:
    - tech_lead@example.com
    - architect@example.com
```

### 3.8 Integración con IA

**Prompt Template para Análisis Estratégico:**

```python
STRATEGIC_ANALYSIS_PROMPT = """
Eres un arquitecto de software senior analizando métricas de arquitectura.

**Contexto del Sistema:**
- Proyecto: {project_name}
- Stack: Python 3.11, {framework}
- Arquitectura declarada: Clean Architecture
- Equipo: {team_size} developers
- Sprint actual: {sprint_id}

**Métricas del Sprint Actual:**
{current_metrics_json}

**Histórico (últimos 6 sprints):**
{historical_metrics_json}

**Análisis Requerido:**

1. **Evaluación de Salud Arquitectónica (0-100)**
   - Puntaje general
   - Desglose por dimensiones: estructura, dependencias, calidad, seguridad

2. **Identificación de Problemas**
   - Críticos (bloqueantes)
   - Importantes (corregir pronto)
   - Menores (backlog)

3. **Análisis de Tendencias**
   - ¿Qué métricas están empeorando?
   - ¿Cuál es la velocidad de deterioro?
   - ¿Qué causas probables?

4. **Predicción (2-3 sprints)**
   - ¿Qué métricas llegarán a umbrales críticos?
   - ¿Qué componentes se volverán unmaintainable?

5. **Recomendaciones Priorizadas**
   - Top 3 acciones inmediatas
   - Esfuerzo estimado (horas)
   - Impacto esperado
   - Riesgo de no hacerlo

6. **Plan Estratégico**
   - Qué hacer en próximo sprint
   - Qué planificar para siguientes 2-3 sprints
   - Cuándo hacer sprint de refactoring

**Formato:**
Markdown estructurado, secciones claras, sin explicaciones obvias.
Enfócate en insights accionables.
"""
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

ArchitectAnalyst usa **SQLite** para almacenar snapshots de métricas:

```python
class MetricsSnapshot:
    id: int
    timestamp: datetime
    sprint_id: str
    project_name: str
    metrics_json: str  # Todas las métricas del sprint

    # Permite análisis de tendencias:
    # - ¿Qué métricas empeoraron vs sprint anterior?
    # - ¿Cuál es la velocidad de deterioro?
    # - ¿Hay patrones estacionales?
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

#### Dashboard Interactivo

A diferencia de CodeGuard (CLI) y DesignReviewer (HTML), ArchitectAnalyst genera **dashboard web interactivo** con Plotly:

- **Gráficos de tendencias** (métricas vs tiempo)
- **Comparación sprint-actual vs histórico**
- **Detección de anomalías** (picos/caídas)
- **Predicción de degradación** (IA)

**Referencia:** Ver `src/quality_agents/architectanalyst/` (implementación futura).

---

## INFRAESTRUCTURA TÉCNICA

### 4.1 Stack Tecnológico

```yaml
Core:
  language: Python 3.11+
  package_manager: pip + venv
  
Analysis Tools:
  static_analysis:
    - flake8
    - pylint
    - bandit
    - mypy
  metrics:
    - radon
    - pydeps
    - coverage.py
    - jscpd
  dependencies:
    - pipdeptree
    - safety
    - pip-audit
    
Quality Platforms (optional but recommended):
  - sonarqube: "Community Edition or Cloud"
  - wily: "For historical metrics"
  
AI:
  provider: Anthropic
  model: claude-sonnet-4
  api: anthropic-sdk
  
Reports:
  html: jinja2
  pdf: weasyprint
  pptx: python-pptx
  charts: plotly / matplotlib
  
CI/CD:
  git_hooks: pre-commit framework
  github_actions: For PR checks
  gitlab_ci: Alternative
  
Notifications:
  email: smtplib
  slack: slack-sdk
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
│   Analyzers   │   │   AI Engine   │   │   Reporters      │
│   (Tools)     │   │   (Claude)    │   │   (HTML/PDF)     │
└───────────────┘   └───────────────┘   └──────────────────┘
        │                   │                    │
        └───────────────────┼────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Database    │
                    │   (History)   │
                    └───────────────┘
```

### 4.3 Estructura de Directorios

```
project_root/
├── .quality_control/
│   ├── codeguard/
│   │   ├── config.yml
│   │   ├── history.log
│   │   └── rules/
│   ├── designreviewer/
│   │   ├── config.yml
│   │   ├── reports/
│   │   └── ai_cache/
│   └── architectanalyst/
│       ├── config.yml
│       ├── reports/
│       ├── dashboards/
│       └── history.db
│
├── .git/
│   └── hooks/
│       ├── pre-commit          # CodeGuard
│       └── pre-push            # Optional light check
│
├── reports/
│   ├── code/                   # CodeGuard logs
│   ├── design/                 # DesignReviewer HTML
│   └── architecture/           # ArchitectAnalyst dashboards
│
└── quality_agents/             # Agent implementations
    ├── __init__.py
    ├── codeguard.py
    ├── designreviewer.py
    ├── architectanalyst.py
    ├── analyzers/
    │   ├── metrics.py
    │   ├── dependencies.py
    │   └── security.py
    ├── ai/
    │   ├── claude_client.py
    │   └── prompts.py
    └── reporters/
        ├── html_generator.py
        ├── pdf_generator.py
        └── dashboard.py
```

### 4.4 Base de Datos de Histórico

**SQLite Schema:**

```sql
-- Metrics history
CREATE TABLE metric_snapshots (
    id INTEGER PRIMARY KEY,
    agent_type TEXT NOT NULL,  -- 'code' | 'design' | 'architecture'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sprint_id TEXT,
    commit_hash TEXT,
    metrics_json TEXT NOT NULL  -- JSON blob with all metrics
);

-- Analysis results
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY,
    snapshot_id INTEGER REFERENCES metric_snapshots(id),
    analysis_type TEXT,  -- 'automated' | 'ai'
    result_json TEXT NOT NULL,
    recommendations_json TEXT
);

-- Exceptions and waivers
CREATE TABLE quality_exceptions (
    id INTEGER PRIMARY KEY,
    metric_name TEXT NOT NULL,
    violation_description TEXT,
    justification TEXT NOT NULL,
    approved_by TEXT NOT NULL,
    approved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    status TEXT DEFAULT 'active'  -- 'active' | 'expired' | 'resolved'
);

-- Trends and predictions
CREATE TABLE trend_analysis (
    id INTEGER PRIMARY KEY,
    metric_name TEXT NOT NULL,
    current_value REAL,
    trend_direction TEXT,  -- 'improving' | 'stable' | 'degrading'
    prediction_3sprints REAL,
    confidence REAL,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## ROADMAP DE IMPLEMENTACIÓN

### Fase 1: MVP - CodeGuard (2-3 semanas)

**Objetivo:** Agente básico funcionando en pre-commit

**Semana 1:**
- [ ] Setup de proyecto y estructura
- [ ] Integración de herramientas básicas (flake8, pylint, bandit)
- [ ] CLI básico para ejecución manual
- [ ] Configuración .codeguard.yml

**Semana 2:**
- [ ] Hook de pre-commit
- [ ] Formato de salida coloreado
- [ ] Sistema de logging
- [ ] Tests unitarios del agente

**Semana 3:**
- [ ] Refinamiento de umbrales
- [ ] Documentación de uso
- [ ] Pruebas con proyectos reales
- [ ] Ajustes basados en feedback

**Entregable:** CodeGuard v1.0 funcionando en tus proyectos

---

### Fase 2: DesignReviewer (3-4 semanas)

**Objetivo:** Análisis profundo con IA

**Semana 1:**
- [ ] Integración de herramientas de diseño (radon, pydeps)
- [ ] Sistema de métricas extendido
- [ ] Lógica de umbrales y bloqueos

**Semana 2:**
- [ ] Integración con Claude API
- [ ] Prompts para refactorización
- [ ] Generación de sugerencias

**Semana 3:**
- [ ] Generador de reportes HTML
- [ ] Visualizaciones (grafos, charts)
- [ ] Sistema de excepciones justificadas

**Semana 4:**
- [ ] Integración con GitHub Actions/GitLab CI
- [ ] Tests e2e
- [ ] Documentación completa
- [ ] Piloto con estudiantes

**Entregable:** DesignReviewer v1.0 con IA

---

### Fase 3: ArchitectAnalyst (4-5 semanas)

**Objetivo:** Dashboard estratégico y análisis predictivo

**Semana 1-2:**
- [ ] Sistema de snapshots y base de datos
- [ ] Calculadores de métricas de Martin
- [ ] Análisis de dependencias completo
- [ ] DSM y Clean Architecture checks

**Semana 3:**
- [ ] Dashboard web interactivo (HTML + JS)
- [ ] Gráficos de tendencias históricos
- [ ] Main Sequence plot
- [ ] Heatmaps de complejidad

**Semana 4:**
- [ ] Análisis predictivo con IA
- [ ] Generación de reportes ejecutivos (PDF, PPTX)
- [ ] Sistema de notificaciones
- [ ] Integración con schedule/cron

**Semana 5:**
- [ ] Tests completos
- [ ] Documentación
- [ ] Deployment guides
- [ ] Presentación y demo

**Entregable:** ArchitectAnalyst v1.0 completo

---

### Fase 4: Integración y Refinamiento (2-3 semanas)

**Objetivo:** Sistema completo integrado y pulido

- [ ] Unificación de configuración
- [ ] Dashboard central que conecta los 3 agentes
- [ ] API REST para consultas externas
- [ ] Integración con otras herramientas (Jira, Notion)
- [ ] Documentación completa del sistema
- [ ] Guías para estudiantes
- [ ] Video tutoriales
- [ ] Paper académico (opcional)

**Entregable:** Quality Control System v1.0

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

**Versión:** 1.0  
**Fecha:** 28 de Diciembre, 2025  
**Autor:** Sistema de Control de Calidad - ISSE  
**Licencia:** MIT (para uso académico y personal)
