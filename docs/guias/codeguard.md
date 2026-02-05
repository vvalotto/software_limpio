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

CodeGuard busca su configuración en estos archivos (en orden de prioridad):

1. `--config` (especificado en línea de comandos)
2. `.codeguard.yml` (en el directorio actual)
3. `configs/codeguard.yml` (configuración por defecto)

### Estructura de Configuración

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

### Formato de Salida

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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary: 2 errors, 2 warnings in 3.2s

⚠️  Commit allowed but review recommended
💡 Run suggested fixes or review manually
```

### Niveles de Severidad

| Icono | Nivel | Descripción | Acción Recomendada |
|-------|-------|-------------|-------------------|
| ✅ | PASS | Sin problemas | Ninguna |
| ℹ️ | INFO | Informativo | Revisar si hay tiempo |
| ⚠️ | WARN | Advertencia | Revisar antes de PR |
| ❌ | ERROR | Error crítico | **Corregir inmediatamente** |

### Qué Verifica CodeGuard

| # | Verificación | Umbral | Severidad |
|---|--------------|--------|-----------|
| 1 | **PEP8** - Estilo de código | 0 violaciones | WARN |
| 2 | **Pylint Score** - Calidad general | ≥ 7.0/10 | WARN |
| 3 | **Imports sin usar** | 0 | WARN |
| 4 | **Funciones inseguras** | 0 | ERROR |
| 5 | **Secretos hardcodeados** | 0 | ERROR |
| 6 | **Bare excepts** | 0 | WARN |
| 7 | **Errores de tipos** | 0 | WARN |
| 8 | **Complejidad ciclomática** | ≤ 10 | INFO |

---

## Opciones Avanzadas

### Línea de Comandos Completa

```bash
codeguard [OPTIONS] PATH

Opciones:
  -c, --config PATH        Archivo de configuración YAML
  -f, --format [text|json] Formato de salida (default: text)
  -v, --verbose            Salida detallada
  -q, --quiet              Solo mostrar errores
  --no-color               Deshabilitar colores
  --version                Mostrar versión
  --help                   Mostrar ayuda
```

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
