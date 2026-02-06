# 🚀 Inicio Rápido - CodeGuard

> **5 minutos para agregar control de calidad automático a tu proyecto Python**

CodeGuard analiza tu código antes de cada commit, detectando problemas de seguridad, estilo y calidad en **menos de 5 segundos**.

---

## 📦 Instalación Rápida

### Opción 1: Desde GitHub (Desarrollo)

```bash
# 1. Clonar repositorio
git clone https://github.com/vvalotto/software_limpio.git
cd software_limpio

# 2. Instalar con pip
pip install -e .

# 3. Verificar instalación
codeguard --version
```

### Opción 2: Desde PyPI (Próximamente)

```bash
pip install quality-agents
codeguard --version
```

---

## ⚡ Uso en 3 Pasos

### Paso 1: Ir a tu proyecto

```bash
cd /ruta/a/tu/proyecto
```

### Paso 2: Crear configuración

Agregar en tu `pyproject.toml`:

```toml
[tool.codeguard]
# Umbrales de calidad
min_pylint_score = 8.0
max_cyclomatic_complexity = 10
max_line_length = 100

# Verificaciones habilitadas
check_pep8 = true
check_pylint = true
check_security = true
check_complexity = true
check_types = true
check_imports = true

# Exclusiones
exclude_patterns = [
    "__pycache__",
    ".venv",
    "venv",
    "migrations",
    "tests/*"
]
```

**¿No tenés pyproject.toml?** Crear archivo `.codeguard.yml` (ver ejemplos en `configs/codeguard.yml`)

### Paso 3: Ejecutar CodeGuard

```bash
# Analizar todo el proyecto
codeguard .

# Analizar directorio específico
codeguard src/

# Analizar archivos específicos
codeguard src/main.py src/utils.py
```

---

## 🎯 Ejemplos de Uso

### Análisis Rápido (< 5 segundos)

```bash
codeguard .
```

### Análisis para Pull Request (~10-15 segundos)

```bash
codeguard --analysis-type pr-review .
```

### Análisis Completo (~20-30 segundos)

```bash
codeguard --analysis-type full .
```

### Salida en JSON (para CI/CD)

```bash
codeguard --format json . > quality-report.json
```

---

## 🔗 Integración con Git (Pre-commit)

### Opción A: Framework pre-commit (Recomendado)

```bash
# 1. Instalar pre-commit
pip install pre-commit

# 2. Crear .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.1.0  # Usar la última versión
    hooks:
      - id: codeguard
        name: CodeGuard Quality Check
EOF

# 3. Instalar hooks
pre-commit install

# 4. Listo! Ahora se ejecutará en cada commit
git add .
git commit -m "Test"
# → CodeGuard se ejecuta automáticamente
```

### Opción B: Hook manual de Git

```bash
# Crear .git/hooks/pre-commit
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running CodeGuard..."
codeguard .
exit 0  # No bloquea el commit, solo advierte
EOF

# Hacer ejecutable
chmod +x .git/hooks/pre-commit
```

---

## 🛡️ Qué Detecta CodeGuard

| Check | Verifica | Ejemplo |
|-------|----------|---------|
| **SecurityCheck** | Hardcoded passwords, eval(), SQL injection | 🔴 CRÍTICO |
| **PEP8Check** | Estilo de código, líneas largas | ⚠️ Advertencia |
| **ComplexityCheck** | Complejidad ciclomática > 10 | ℹ️ Info |
| **PylintCheck** | Score general < 8.0/10 | ⚠️ Advertencia |
| **TypeCheck** | Type hints faltantes | ⚠️ Advertencia |
| **ImportCheck** | Imports sin usar | ⚠️ Advertencia |

---

## 📊 Ejemplo de Output

```
╭─────────────────────────────────────────────────────────────╮
│               🛡️  CodeGuard Quality Report                  │
│  📊 Files: 5 | Issues: 8 (2 errors, 6 warnings)            │
│  ⏱️  Execution time: 2.8s                                   │
╰─────────────────────────────────────────────────────────────╯

❌ ERRORS (2)
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File              ┃ Line  ┃ Issue                       ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ src/auth.py       │ 45    │ Hardcoded password detected │
│ src/api.py        │ 78    │ Use of eval() is dangerous  │
└───────────────────┴───────┴─────────────────────────────┘

⚠️  WARNINGS (6)
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File              ┃ Line  ┃ Issue                       ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ src/models.py     │ 23    │ Pylint score 7.2/10         │
│ src/utils.py      │ 156   │ Unused import: os           │
...

💡 Suggestions:
  Security: Use environment variables for secrets
  Style: Run black src/ --line-length 100
  Imports: Run autoflake --remove-unused-variables
```

---

## 🎓 Próximos Pasos

1. ✅ **Instalar CodeGuard**
2. ✅ **Ejecutar en tu proyecto**
3. ✅ **Revisar problemas detectados**
4. 📖 **Leer la [Guía Completa](docs/guias/codeguard.md)**
5. 🔧 **Configurar pre-commit hooks**
6. 🤖 **Explorar [Configuración de IA](docs/guias/codeguard.md#configuración-de-ia-opcional)** (opcional)

---

## 📚 Documentación Completa

- **[Guía de Usuario](docs/guias/codeguard.md)** - Documentación completa
- **[Ejemplo Funcional](examples/sample_project/)** - Proyecto con problemas detectables
- **[Documentación Técnica](src/quality_agents/codeguard/README.md)** - Para contribuidores
- **[Preguntas Frecuentes](docs/guias/codeguard.md#preguntas-frecuentes)** - FAQ

---

## 🆘 Ayuda Rápida

### ¿CodeGuard bloquea mis commits?

**No.** Solo advierte. Podés hacer commit incluso con errores.

### ¿Cuánto tarda?

**< 5 segundos** en proyectos medianos (análisis pre-commit).

### ¿Cómo deshabilito un check?

En `pyproject.toml`:
```toml
[tool.codeguard]
check_pep8 = false  # Deshabilitar PEP8
```

### ¿Cómo excluir archivos?

En `pyproject.toml`:
```toml
[tool.codeguard]
exclude_patterns = ["tests/*", "migrations/*", "*.bak"]
```

### ¿Funciona con Python 2.7?

**No.** Requiere **Python 3.11+**.

---

## 🐛 Problemas?

[Reportar issue](https://github.com/vvalotto/software_limpio/issues)

---

**Software Limpio** - Control de Calidad Automatizado para Python 🚀
