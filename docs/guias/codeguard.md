# Guía de Uso - CodeGuard

> Agente de control de calidad rápido para pre-commit

**CodeGuard** es una herramienta de análisis de código que se ejecuta antes de cada commit para detectar problemas de calidad, seguridad y estilo. **No bloquea tus commits**, solo te advierte de problemas potenciales.

---

## Índice

1. [Instalación](#instalación)
2. [Uso Básico](#uso-básico)
3. [Configuración](#configuración)
4. [Interpretación de Resultados](#interpretación-de-resultados)
5. [Opciones Avanzadas](#opciones-avanzadas)
6. [Integración con Git](#integración-con-git)
7. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Instalación

### Requisitos

- Python 3.11 o superior
- Git (para integración con hooks)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/vvalotto/software_limpio.git
cd software_limpio

# 2. Crear entorno virtual
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instalar en modo desarrollo
pip install -e ".[dev]"

# 4. Verificar instalación
codeguard --version
```

---

## Uso Básico

### Analizar Directorio Actual

```bash
codeguard .
```

### Analizar Directorio Específico

```bash
codeguard src/
codeguard src/quality_agents/
```

### Analizar Archivos Específicos

```bash
codeguard src/main.py
codeguard src/module1.py src/module2.py
```

### Usar Configuración Personalizada

```bash
codeguard --config configs/codeguard.yml .
```

### Salida en Formato JSON

```bash
codeguard --format json . > report.json
```

---

## Configuración

CodeGuard soporta dos formatos de configuración:

### Opción 1: pyproject.toml (Recomendado)

La forma moderna y estándar de configurar herramientas Python según [PEP 518](https://peps.python.org/pep-0518/).

Agregar en tu `pyproject.toml`:

```toml
[tool.codeguard]
# Umbrales de calidad
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

# Exclusiones
exclude_patterns = [
    "*.pyc",
    "__pycache__",
    ".venv",
    "venv",
    "migrations",
    "tests/*"
]

# Configuración de IA (opcional)
[tool.codeguard.ai]
enabled = false              # Cambiar a true para habilitar sugerencias con IA
explain_errors = true        # IA explica los errores detectados
suggest_fixes = true         # IA sugiere correcciones
max_tokens = 500            # Máximo de tokens por respuesta
```

**Ventajas:**
- ✅ Un solo archivo para todas las herramientas del proyecto
- ✅ Estándar de la comunidad Python
- ✅ Compatible con pip, black, pytest, mypy, etc.

### Opción 2: Archivo YAML

Crear archivo `.codeguard.yml` en la raíz de tu proyecto:

```yaml
# Umbrales de calidad
min_pylint_score: 8.0
max_cyclomatic_complexity: 10
max_line_length: 100
max_function_lines: 20

# Verificaciones habilitadas
check_pep8: true
check_pylint: true
check_security: true
check_complexity: true
check_types: true
check_imports: true

# Exclusiones
exclude_patterns:
  - "*.pyc"
  - "__pycache__"
  - ".venv"
  - "venv"
  - "migrations"
  - "tests/*"
```

### Búsqueda Automática de Configuración

CodeGuard busca su configuración en este orden (se usa el primero que encuentre):

1. `--config PATH` (especificado en línea de comandos)
2. `pyproject.toml` → `[tool.codeguard]` (directorio actual y padres)
3. `.codeguard.yml` (directorio actual)
4. `configs/codeguard.yml` (configuración por defecto del paquete)

Si no encuentra ninguno, usa valores por defecto seguros.

### Personalización de Umbrales

**Proyecto Pequeño (más estricto):**
```yaml
min_pylint_score: 9.0
max_cyclomatic_complexity: 5
max_function_lines: 15
```

**Proyecto Legacy (más permisivo):**
```yaml
min_pylint_score: 6.0
max_cyclomatic_complexity: 15
max_function_lines: 30
```

---

## Interpretación de Resultados

### Formato de Salida (Rich Formatter)

CodeGuard usa [Rich](https://rich.readthedocs.io/) para mostrar resultados profesionales con colores y tablas:

```
╭─────────────────────────────────────────────────────────────────────╮
│                    🛡️  CodeGuard Quality Report                     │
│                                                                     │
│  📊 Analysis Summary                                                │
│  • Files analyzed: 5                                                │
│  • Total issues: 8 (2 errors, 4 warnings, 2 info)                  │
│  • Execution time: 2.8s                                             │
╰─────────────────────────────────────────────────────────────────────╯

❌ ERRORS (2)
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File              ┃ Line  ┃ Issue                               ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ src/auth.py       │ 45    │ Hardcoded password detected         │
│ src/utils/api.py  │ 78    │ Use of insecure function: eval()    │
└───────────────────┴───────┴─────────────────────────────────────┘

⚠️  WARNINGS (4)
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File              ┃ Line  ┃ Issue                               ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ src/models.py     │ 23    │ Pylint score 7.2/10 (threshold 8.0) │
│ src/utils/db.py   │ 156   │ Unused import: os                   │
│ src/core/app.py   │ 89    │ Complexity 12 (threshold 10)        │
│ src/handlers.py   │ 45    │ Missing type hint for parameter     │
└───────────────────┴───────┴─────────────────────────────────────┘

💡 Suggestions

  Security Issues:
    Run: pip install python-decouple && use config() for secrets

  Code Quality:
    Run: black src/ --line-length 100
    Run: autoflake --remove-unused-variables --in-place src/utils/db.py

  Type Safety:
    Run: mypy src/ --install-types

✅ Analysis complete! Review issues before committing.
```

### Formato JSON

Para integración con CI/CD o procesamiento automatizado:

```bash
codeguard --format json . > report.json
```

Estructura del JSON:

```json
{
  "summary": {
    "total_files": 5,
    "total_issues": 8,
    "errors": 2,
    "warnings": 4,
    "info": 2,
    "execution_time": 2.8
  },
  "results": [
    {
      "check_name": "SecurityCheck",
      "severity": "ERROR",
      "message": "Hardcoded password detected",
      "file_path": "src/auth.py",
      "line_number": 45
    }
  ],
  "by_severity": {
    "ERROR": 2,
    "WARNING": 4,
    "INFO": 2
  },
  "timestamp": "2026-02-05T10:30:45"
}
```

### Niveles de Severidad

| Icono | Nivel | Descripción | Acción Recomendada |
|-------|-------|-------------|-------------------|
| ✅ | PASS | Sin problemas | Ninguna |
| ℹ️ | INFO | Informativo | Revisar si hay tiempo |
| ⚠️ | WARN | Advertencia | Revisar antes de PR |
| ❌ | ERROR | Error crítico | **Corregir inmediatamente** |

### Qué Verifica CodeGuard

CodeGuard usa una **arquitectura modular** con 6 checks independientes que se ejecutan según el contexto:

| Check | Herramienta | Verifica | Prioridad | Tiempo | Severidad |
|-------|-------------|----------|-----------|--------|-----------|
| **PEP8Check** | flake8 | Estilo de código PEP8 | 2 | ~0.5s | WARNING |
| **SecurityCheck** | bandit | Vulnerabilidades, secretos, funciones inseguras | 1 | ~1.5s | ERROR |
| **ComplexityCheck** | radon | Complejidad ciclomática, anidamiento | 3 | ~1.0s | INFO/WARNING |
| **PylintCheck** | pylint | Calidad general, score | 4 | ~2.0s | WARNING |
| **TypeCheck** | mypy | Tipos, anotaciones | 5 | ~3.0s | WARNING |
| **ImportCheck** | pylint | Imports sin usar, duplicados | 6 | ~0.5s | WARNING |

**Prioridad:** 1 = más crítico (se ejecuta primero)

**Checks ejecutados según análisis:**
- `pre-commit`: Priority 1-3 (PEP8, Security, Complexity) → < 5s
- `pr-review`: Priority 1-5 (+ Pylint, Types) → ~10-15s
- `full`: Priority 1-6 (todos los checks) → ~20-30s

### Detalles de Cada Check

#### 1. PEP8Check (flake8)
- Espaciado incorrecto
- Líneas muy largas (> 100 caracteres)
- Imports desordenados
- Nombres de variables no conformes

#### 2. SecurityCheck (bandit)
- 🔴 **ERROR:** Hardcoded passwords/secrets
- 🔴 **ERROR:** Uso de `eval()`, `exec()`
- 🔴 **ERROR:** SQL injection potencial
- ⚠️ **WARNING:** Uso de `assert` en producción
- ⚠️ **WARNING:** Módulos inseguros (pickle, yaml.load)

#### 3. ComplexityCheck (radon)
- Complejidad ciclomática > 10
- Funciones muy largas (> 20 líneas)
- Anidamiento profundo (> 4 niveles)

#### 4. PylintCheck
- Score general < 8.0/10
- Code smells detectados
- Variables sin usar
- Docstrings faltantes

#### 5. TypeCheck (mypy)
- Errores de tipos
- Type hints faltantes
- Incompatibilidades de tipos

#### 6. ImportCheck
- Imports sin usar
- Imports duplicados
- Imports dentro de funciones

---

## Opciones Avanzadas

### Línea de Comandos Completa

```bash
codeguard [OPTIONS] PATH

Opciones:
  -c, --config PATH                    Archivo de configuración
  -f, --format [text|json]             Formato de salida (default: text)
  --analysis-type [pre-commit|pr-review|full]  Tipo de análisis (default: pre-commit)
  --time-budget FLOAT                  Presupuesto de tiempo en segundos
  -v, --verbose                        Salida detallada
  -q, --quiet                          Solo mostrar errores
  --no-color                           Deshabilitar colores
  --version                            Mostrar versión
  --help                               Mostrar ayuda
```

### Tipos de Análisis (--analysis-type)

CodeGuard adapta qué checks ejecuta según el contexto:

| Tipo | Uso | Checks | Tiempo | Prioridad |
|------|-----|--------|--------|-----------|
| `pre-commit` | Commits rápidos | Solo checks críticos (priority 1-3) | < 5s | Default |
| `pr-review` | Pull Requests | Checks importantes (priority 1-5) | ~10-15s | Completo |
| `full` | Análisis completo | Todos los checks (priority 1-6) | ~20-30s | Exhaustivo |

**Ejemplos:**

```bash
# Análisis rápido para commit (default)
codeguard .
codeguard --analysis-type pre-commit .

# Análisis para PR review
codeguard --analysis-type pr-review .

# Análisis completo exhaustivo
codeguard --analysis-type full .
```

### Presupuesto de Tiempo (--time-budget)

Limita el tiempo total de ejecución. CodeGuard ejecuta solo los checks que caben en el presupuesto.

```bash
# Máximo 3 segundos (ultra rápido)
codeguard --time-budget 3.0 .

# Máximo 10 segundos (balanceado)
codeguard --time-budget 10.0 .
```

**Nota:** El orquestador selecciona checks por prioridad hasta agotar el presupuesto.

### Ejemplos Prácticos

**Análisis silencioso (solo errores):**
```bash
codeguard --quiet src/
```

**Análisis detallado con colores:**
```bash
codeguard --verbose --format text .
```

**Generar reporte JSON para CI/CD:**
```bash
codeguard --format json --no-color . > quality-report.json
```

**Analizar solo archivos modificados (Git):**
```bash
codeguard $(git diff --name-only --cached | grep '\.py$')
```

---

## Configuración de IA (Opcional)

CodeGuard puede usar **Claude API** para explicar errores y sugerir correcciones de forma inteligente. Esta funcionalidad es **opt-in** (deshabilitada por defecto).

### Habilitar IA

En tu `pyproject.toml`:

```toml
[tool.codeguard.ai]
enabled = true                          # Habilitar sugerencias con IA
explain_errors = true                   # IA explica los errores
suggest_fixes = true                    # IA sugiere correcciones
max_tokens = 500                        # Máximo de tokens por respuesta
```

O en `.codeguard.yml`:

```yaml
ai:
  enabled: true
  explain_errors: true
  suggest_fixes: true
  max_tokens: 500
```

### Configurar API Key

```bash
# Opción 1: Variable de entorno (recomendado)
export ANTHROPIC_API_KEY="sk-ant-..."

# Opción 2: Archivo .env en la raíz del proyecto
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

**⚠️ IMPORTANTE:** Nunca commitees tu API key. Agregar `.env` a `.gitignore`.

### Ejemplo de Output con IA

```
❌ ERROR: Hardcoded password detected (line 45)
   File: src/auth.py

💡 AI Explanation:
   Hardcoded credentials in source code are a critical security risk. If the
   code is pushed to a repository, the password becomes publicly accessible.

🔧 Suggested Fix:
   1. Use environment variables:
      password = os.getenv('DB_PASSWORD')

   2. Or use a secrets management tool:
      from decouple import config
      password = config('DB_PASSWORD')

   3. Add .env to .gitignore to prevent accidental commits
```

### Costos y Límites

- Modelo Sonnet: ~$3 por millón de tokens de entrada
- CodeGuard usa ~100-300 tokens por análisis (con errores)
- Análisis típico: < $0.001 USD

### Desactivar IA Temporalmente

```bash
# Sin cambiar configuración
ANTHROPIC_API_KEY="" codeguard .

# O modificar pyproject.toml
[tool.codeguard.ai]
enabled = false
```

### FAQ de IA

**¿Mis archivos se envían a Claude?**
Solo los mensajes de error y fragmentos de código relevantes, no todo el archivo.

**¿Funciona sin IA?**
Sí, CodeGuard funciona perfectamente sin IA. Solo pierde las explicaciones inteligentes.

**¿Aumenta el tiempo de ejecución?**
~2-3 segundos adicionales si hay errores. Si no hay errores, no hay overhead.

---

## Integración con Git

### Opción 1: Pre-commit Framework (Recomendado)

CodeGuard se integra con el [framework pre-commit](https://pre-commit.com/), la forma moderna y estándar de gestionar hooks de Git.

#### Instalación

```bash
# 1. Instalar pre-commit en tu proyecto
pip install pre-commit

# 2. Crear archivo .pre-commit-config.yaml en la raíz del proyecto
cat > .pre-commit-config.yaml << 'EOF'
repos:
  # CodeGuard - Análisis rápido para commits
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.1.0  # Usar la última versión
    hooks:
      - id: codeguard
        name: CodeGuard Quality Check
        args: ['--format', 'text']

  # Hooks opcionales adicionales
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        args: [--line-length=100]

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile, black]
EOF

# 3. Instalar los hooks en tu repositorio Git
pre-commit install

# 4. (Opcional) Ejecutar en todos los archivos
pre-commit run --all-files
```

#### Hooks Disponibles

CodeGuard proporciona 3 hooks diferentes:

| Hook ID | Descripción | Uso | Tiempo |
|---------|-------------|-----|--------|
| `codeguard` | Análisis rápido (default) | Pre-commit | < 5s |
| `codeguard-pr` | Análisis para PR review | Pre-push / Manual | ~10-15s |
| `codeguard-full` | Análisis completo | Manual | ~20-30s |

#### Ejemplos de Configuración

**Análisis rápido (solo pre-commit):**
```yaml
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.1.0
    hooks:
      - id: codeguard
```

**Análisis completo en pre-push:**
```yaml
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.1.0
    hooks:
      - id: codeguard         # Pre-commit rápido
      - id: codeguard-pr      # Pre-push completo
        stages: [push]
```

**Solo análisis manual:**
```yaml
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.1.0
    hooks:
      - id: codeguard-full
        stages: [manual]
```

#### Comandos Útiles

```bash
# Ejecutar todos los hooks manualmente
pre-commit run --all-files

# Ejecutar solo CodeGuard
pre-commit run codeguard --all-files

# Ejecutar análisis completo
pre-commit run codeguard-full --all-files

# Saltar hooks en un commit (no recomendado)
git commit --no-verify -m "Mensaje"

# Actualizar versiones de hooks
pre-commit autoupdate
```

#### Ventajas del Framework pre-commit

- ✅ Gestión centralizada de hooks en `.pre-commit-config.yaml`
- ✅ Actualización automática de versiones
- ✅ Aislamiento de dependencias (entornos virtuales por hook)
- ✅ Fácil compartir configuración con el equipo
- ✅ Integración con CI/CD
- ✅ No requiere scripts bash manuales

---

### Opción 2: Hooks Manuales de Git

Si preferís no usar el framework pre-commit, podés crear hooks de Git tradicionales.

#### Pre-commit Hook Manual

Crear archivo `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Ejecutar CodeGuard antes de cada commit
echo "Running CodeGuard quality checks..."

# Obtener archivos Python modificados
PYTHON_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -n "$PYTHON_FILES" ]; then
    codeguard $PYTHON_FILES

    # Nota: CodeGuard no bloquea, solo advierte
    # Si querés bloquear en caso de errores, descomentar:
    # if [ $? -ne 0 ]; then
    #     echo "❌ Quality checks failed. Commit blocked."
    #     exit 1
    # fi
fi

echo "✅ Quality checks completed"
exit 0
```

Hacer el hook ejecutable:
```bash
chmod +x .git/hooks/pre-commit
```

#### Pre-push Hook Manual

Crear archivo `.git/hooks/pre-push`:

```bash
#!/bin/bash

echo "Running full CodeGuard analysis before push..."
codeguard .

# Bloquear push si hay errores críticos
if [ $? -ne 0 ]; then
    read -p "Quality issues found. Push anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

exit 0
```

**Limitaciones de hooks manuales:**
- ❌ No se comparten en el repositorio (están en `.git/hooks/`)
- ❌ Cada desarrollador debe crearlos manualmente
- ❌ Difícil mantener versiones sincronizadas
- ❌ No hay gestión de dependencias automática

---

## Troubleshooting Pre-commit

### El hook no se ejecuta

```bash
# Verificar que los hooks estén instalados
ls -la .git/hooks/pre-commit

# Reinstalar hooks
pre-commit install
```

### Error "command not found: codeguard"

El hook intenta ejecutar `codeguard` pero no lo encuentra. Soluciones:

```bash
# Opción 1: Instalar software_limpio en el entorno de pre-commit
# Agregar en .pre-commit-config.yaml:
repos:
  - repo: local
    hooks:
      - id: codeguard
        name: CodeGuard Quality Check
        entry: codeguard
        language: system  # Usa el codeguard instalado localmente
        types: [python]
        args: ['--analysis-type', 'pre-commit']

# Opción 2: Especificar el path completo
# Si instalaste en un venv específico
entry: /path/to/.venv/bin/codeguard
```

### Pre-commit tarda mucho

```bash
# Ver qué hooks están tomando tiempo
pre-commit run --all-files --verbose

# Usar solo el hook rápido de CodeGuard
# En .pre-commit-config.yaml:
hooks:
  - id: codeguard  # < 5s
  # Evitar:
  # - id: codeguard-full  # ~30s
```

### Quiero saltar CodeGuard solo una vez

```bash
# Saltar todos los hooks (no recomendado)
git commit --no-verify -m "Mensaje"

# Mejor: deshabilitar temporalmente CodeGuard
# Comentar en .pre-commit-config.yaml:
# - id: codeguard
```

### Actualizar CodeGuard a nueva versión

```bash
# En .pre-commit-config.yaml, cambiar:
# rev: v0.1.0  → rev: v0.2.0

# Luego ejecutar:
pre-commit autoupdate
pre-commit clean  # Limpiar caché si hay problemas
```

---

## Preguntas Frecuentes

### ¿CodeGuard bloquea mis commits?

**No.** CodeGuard solo advierte. Podés hacer commit incluso con errores. Sin embargo, se recomienda corregir problemas críticos (❌ ERROR) antes de hacer push.

### ¿Cuánto tiempo tarda?

CodeGuard está diseñado para ejecutarse en **menos de 5 segundos** en proyectos medianos. Si tarda más, considerá:
- Reducir el alcance del análisis
- Excluir directorios grandes (tests, migrations)
- Ajustar las verificaciones habilitadas

### ¿Puedo usar CodeGuard sin Git?

Sí. CodeGuard funciona como herramienta standalone:
```bash
codeguard /path/to/proyecto
```

### ¿Cómo deshabilito una verificación específica?

En tu `.codeguard.yml`:
```yaml
check_pep8: false        # Deshabilitar PEP8
check_complexity: false  # Deshabilitar complejidad
```

### ¿Cómo excluir archivos o directorios?

En tu `.codeguard.yml`:
```yaml
exclude_patterns:
  - "tests/*"
  - "migrations/*"
  - "legacy_module.py"
  - "*.bak"
```

### ¿CodeGuard autocorrige problemas?

No directamente. Pero sugiere comandos para autocorrección:
- `black` para formateo
- `autoflake` para imports sin usar
- `isort` para ordenar imports

### ¿Puedo usar CodeGuard en CI/CD?

Sí. Ejemplo para GitHub Actions:

```yaml
- name: Run CodeGuard
  run: |
    pip install -e .
    codeguard --format json . > quality-report.json
```

### ¿Funciona con Python 2.7?

No. CodeGuard requiere **Python 3.11+** para funcionar correctamente.

### ¿Debo usar pyproject.toml o .codeguard.yml?

**Recomendado:** `pyproject.toml` con `[tool.codeguard]`
- Es el estándar moderno de Python (PEP 518)
- Un solo archivo para todas las herramientas
- Compatible con pip, black, pytest, mypy, etc.

Usa `.codeguard.yml` solo si tu proyecto no tiene `pyproject.toml`.

### ¿Qué diferencia hay entre pre-commit, pr-review y full?

Son **tipos de análisis** que ejecutan diferentes checks:
- `pre-commit`: Solo checks críticos (< 5s) - Para commits rápidos
- `pr-review`: Checks importantes (~10-15s) - Para pull requests
- `full`: Todos los checks (~20-30s) - Análisis exhaustivo

Ejemplo: `codeguard --analysis-type pr-review .`

### ¿Los checks se ejecutan en paralelo?

No actualmente. Se ejecutan secuencialmente por prioridad. Esto simplifica el debugging y evita race conditions.

### ¿Cómo sé qué checks se ejecutaron?

En el output JSON, la clave `results` muestra todos los checks ejecutados:
```bash
codeguard --format json . | jq '.results[].check_name' | sort -u
```

### ¿Puedo crear mis propios checks?

Sí, gracias a la arquitectura modular. Ver sección [Arquitectura Modular](#arquitectura-modular-para-contribuidores).

---

## Arquitectura Modular (Para Contribuidores)

CodeGuard usa una **arquitectura modular** que facilita agregar nuevos checks sin modificar el código core.

### Componentes Principales

```
src/quality_agents/codeguard/
├── agent.py              # CLI y coordinación
├── config.py             # Configuración (pyproject.toml/YAML)
├── orchestrator.py       # Orquestador contextual
├── formatter.py          # Rich formatter + JSON
└── checks/               # Checks modulares (auto-discovery)
    ├── pep8_check.py
    ├── security_check.py
    ├── complexity_check.py
    ├── pylint_check.py
    ├── type_check.py
    └── import_check.py
```

### Patrón Verifiable

Todos los checks heredan de la clase base `Verifiable`:

```python
from quality_agents.shared.verifiable import Verifiable, ExecutionContext

class MyCheck(Verifiable):
    @property
    def name(self) -> str:
        return "MyCheck"

    @property
    def priority(self) -> int:
        return 3  # 1 = más crítico

    @property
    def estimated_duration(self) -> float:
        return 1.0  # segundos

    def should_run(self, context: ExecutionContext) -> bool:
        # Decide si debe ejecutarse según contexto
        return context.analysis_type == "full"

    def execute(self, file_path: Path) -> List[CheckResult]:
        # Implementa la verificación
        results = []
        # ... lógica del check ...
        return results
```

### Orquestación Contextual

El `CheckOrchestrator` selecciona checks según:
- **Tipo de análisis** (pre-commit, pr-review, full)
- **Presupuesto de tiempo** (--time-budget)
- **Prioridad** del check
- **Contexto del archivo** (nuevo, modificado, excluido)

### Agregar un Nuevo Check

1. Crear archivo en `checks/mi_check.py`
2. Heredar de `Verifiable`
3. Implementar métodos requeridos
4. Exportar en `checks/__init__.py`
5. **Auto-discovery hace el resto** ✨

No se requiere modificar `agent.py` u `orchestrator.py`.

### Documentación Técnica

- [Decisión Arquitectónica](../agentes/decision_arquitectura_checks_modulares.md)
- [Guía de Implementación](../agentes/guia_implementacion_agentes.md)
- [Especificación Completa](../agentes/especificacion_agentes_calidad.md)

---

## Próximos Pasos

Una vez que domines CodeGuard, explorá los otros agentes:

- **DesignReviewer** - Análisis profundo de diseño para PRs (próximamente)
- **ArchitectAnalyst** - Tendencias de arquitectura a largo plazo (próximamente)

---

## Recursos Adicionales

- [Especificación Técnica de CodeGuard](../agentes/especificacion_agentes_calidad.md#agente-de-código---codeguard)
- [Catálogo de Métricas de Código](../metricas/metricas_codigo.md)
- [Principios de Código Limpio](../teoria/trilogia_limpia/codigo_limpio.md)
- [Configuración de Ejemplo](../../configs/codeguard.yml)

---

## Soporte

¿Encontraste un problema? [Reportar issue](https://github.com/vvalotto/software_limpio/issues)

---

[← Volver a Guías](README.md)
