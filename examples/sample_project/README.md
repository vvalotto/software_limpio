# Sample Project - Ejemplo de CodeGuard

> Proyecto de ejemplo que demuestra cómo usar CodeGuard para detectar problemas de calidad en código Python

Este proyecto contiene **intencionalmente** código con diversos problemas de calidad para demostrar cómo CodeGuard los detecta y reporta.

---

## 📋 Contenido

Este proyecto incluye archivos con diferentes tipos de problemas:

| Archivo | Problemas Demostrados |
|---------|----------------------|
| `src/calculator.py` | ✅ Código limpio + complejidad alta |
| `src/security_issues.py` | 🔴 Hardcoded passwords, eval(), SQL injection, etc. |
| `src/style_issues.py` | ⚠️ Violaciones de PEP8, líneas largas, mal espaciado |
| `src/imports_and_types.py` | ⚠️ Imports sin usar, type hints faltantes |

---

## 🚀 Uso

### Opción 1: Ejecutar CodeGuard Directamente

```bash
# Desde la raíz del repositorio software_limpio
cd examples/sample_project

# Análisis rápido (pre-commit)
codeguard .

# Análisis completo
codeguard --analysis-type full .

# Salida en JSON
codeguard --format json . | jq
```

### Opción 2: Usar el Script de Demo

```bash
# Ejecutar demostración completa
chmod +x demo.sh
./demo.sh
```

El script ejecutará:
1. Análisis pre-commit (< 5s)
2. Análisis PR-review (~10-15s)
3. Análisis completo (~20-30s)
4. Output en JSON

### Opción 3: Integrar con Pre-commit Framework

```bash
# 1. Instalar pre-commit
pip install pre-commit

# 2. Instalar los hooks
pre-commit install

# 3. Ejecutar manualmente en todos los archivos
pre-commit run --all-files

# 4. Ahora se ejecutará automáticamente en cada commit
git add src/calculator.py
git commit -m "Test commit"
# → CodeGuard se ejecutará automáticamente
```

---

## 🔍 Qué Detecta CodeGuard

### SecurityCheck (Prioridad 1 - Crítico)

**Archivo:** `src/security_issues.py`

- 🔴 **ERROR:** Hardcoded password en línea 11
- 🔴 **ERROR:** Uso de `eval()` en línea 17
- 🔴 **ERROR:** SQL injection en línea 34
- 🔴 **ERROR:** Uso de `exec()` en línea 54
- ⚠️ **WARNING:** Uso inseguro de `pickle.load()`
- ⚠️ **WARNING:** Uso de `yaml.load()` sin `safe_load()`
- ⚠️ **WARNING:** Assert en código de producción

### PEP8Check (Prioridad 2)

**Archivo:** `src/style_issues.py`

- ⚠️ **WARNING:** Líneas muy largas (> 100 caracteres)
- ⚠️ **WARNING:** Espaciado incorrecto en funciones
- ⚠️ **WARNING:** Nombres de variables no conformes (PascalCase)
- ⚠️ **WARNING:** Import en mitad del archivo
- ⚠️ **WARNING:** Múltiples statements en una línea
- ⚠️ **WARNING:** Comparación incorrecta con None/True/False

### ComplexityCheck (Prioridad 3)

**Archivo:** `src/calculator.py`

- ℹ️ **INFO:** Función `complex_calculation()` con CC ≥ 8
- ℹ️ **INFO:** Clase `GodCalculator` con muchos métodos (WMC alto)

### ImportCheck (Prioridad 6)

**Archivo:** `src/imports_and_types.py`

- ⚠️ **WARNING:** Import `os` sin usar
- ⚠️ **WARNING:** Import `sys` sin usar
- ⚠️ **WARNING:** Import `json` sin usar
- ⚠️ **WARNING:** Imports duplicados

### TypeCheck (Prioridad 5)

**Archivo:** `src/imports_and_types.py`

- ⚠️ **WARNING:** Función sin type hints
- ⚠️ **WARNING:** Función puede retornar None pero no indica Optional
- ⚠️ **WARNING:** Tipo incorrecto en retorno (str en lugar de float)

---

## 🎯 Ejemplo de Output

### Modo Text (Rich Formatter)

```
╭─────────────────────────────────────────────────────────────╮
│               🛡️  CodeGuard Quality Report                  │
│  📊 Files: 4 | Issues: 23 (8 errors, 15 warnings)         │
╰─────────────────────────────────────────────────────────────╯

❌ ERRORS (8)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File                     ┃ Line ┃ Issue                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ src/security_issues.py   │ 11   │ Hardcoded password      │
│ src/security_issues.py   │ 17   │ Use of eval()           │
...

💡 Suggestions:
  Security: Use environment variables for secrets
  Style: Run black src/ --line-length 100
  Imports: Run autoflake --remove-unused-variables
```

### Modo JSON

```json
{
  "summary": {
    "total_files": 4,
    "total_issues": 23,
    "errors": 8,
    "warnings": 15,
    "execution_time": 2.8
  },
  "results": [
    {
      "check_name": "SecurityCheck",
      "severity": "ERROR",
      "message": "Hardcoded password detected",
      "file_path": "src/security_issues.py",
      "line_number": 11
    }
  ]
}
```

---

## ⚙️ Configuración

### pyproject.toml

El archivo `pyproject.toml` incluye configuración de CodeGuard:

```toml
[tool.codeguard]
min_pylint_score = 7.0
max_cyclomatic_complexity = 10
check_pep8 = true
check_security = true
exclude_patterns = ["*.pyc", "__pycache__"]

[tool.codeguard.ai]
enabled = false  # Cambiar a true si tienes ANTHROPIC_API_KEY
```

### Habilitar IA (Opcional)

```bash
# 1. Configurar API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 2. Habilitar en pyproject.toml
[tool.codeguard.ai]
enabled = true

# 3. Ejecutar CodeGuard
codeguard .
# → Recibirás explicaciones inteligentes de errores
```

---

## 🛠️ Corregir Problemas

### Automático

```bash
# Formatear código con black
black src/ --line-length 100

# Ordenar imports
isort src/ --profile black

# Eliminar imports sin usar
autoflake --remove-unused-variables --in-place src/*.py
```

### Manual

1. **Seguridad:** Usar variables de entorno para secretos
2. **Complejidad:** Refactorizar funciones largas
3. **Tipos:** Agregar type hints con mypy

---

## 📚 Documentación

- [Guía de Usuario Completa](../../docs/guias/codeguard.md)
- [README Principal](../../README.md)
- [Documentación Técnica](../../src/quality_agents/codeguard/README.md)

---

## 💡 Próximos Pasos

1. Ejecuta CodeGuard en este proyecto
2. Revisa los problemas detectados
3. Intenta corregir algunos problemas
4. Re-ejecuta CodeGuard para verificar
5. Integra CodeGuard en tus propios proyectos

---

**Software Limpio** - Framework de Control de Calidad para Python
