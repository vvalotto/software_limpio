# Software Limpio

Repositorio de conocimiento sobre calidad de diseño de software en la era de la IA.

## Propósito

Completar la trilogía de Robert C. Martin (Clean Code, Clean Architecture) con **Clean Design**: los fundamentos de diseño que son independientes del paradigma de programación y anteriores a la orientación a objetos.

## Tesis Central

La IA transforma al profesional de software de "escritor de código" a **director y evaluador de calidad**, usando métricas como herramientas objetivas de verificación.

---

## 🚀 Quick Start - CodeGuard

**CodeGuard** es el primer agente implementado: análisis de calidad rápido para pre-commit.

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/vvalotto/software_limpio.git
cd software_limpio

# Instalar en modo desarrollo
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Verificar instalación
codeguard --help
```

### Uso Básico

```bash
# Analizar proyecto actual
codeguard .

# Análisis para PR review
codeguard --analysis-type pr-review .

# Salida en JSON
codeguard --format json . > report.json
```

### Ejemplo de Output

```
╭─────────────────────────────────────────────────────────────╮
│               🛡️  CodeGuard Quality Report                  │
│  📊 Files: 5 | Issues: 8 (2 errors, 4 warnings) | 2.8s    │
╰─────────────────────────────────────────────────────────────╯

❌ ERRORS (2)
┃ src/auth.py:45      │ Hardcoded password detected
┃ src/utils/api.py:78 │ Use of insecure function: eval()

💡 Suggestions: Run black, fix security issues
```

### Integración con Git

```bash
# Opción 1: Pre-commit Framework (recomendado)
pip install pre-commit
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.1.0
    hooks:
      - id: codeguard
EOF
pre-commit install

# Opción 2: Hook manual
# Ver guía completa en docs/guias/codeguard.md
```

### Configuración

En tu `pyproject.toml`:

```toml
[tool.codeguard]
min_pylint_score = 8.0
max_cyclomatic_complexity = 10
check_pep8 = true
check_security = true
exclude_patterns = ["tests/*", "migrations/*"]
```

### Documentación Completa

📖 **[Guía de Usuario Completa](docs/guias/codeguard.md)** - Instalación, configuración, integración con Git, FAQ

🔧 **[README Técnico](src/quality_agents/codeguard/README.md)** - Arquitectura modular, cómo contribuir

📋 **[Plan de Implementación](src/quality_agents/codeguard/PLAN_IMPLEMENTACION.md)** - Roadmap y progreso

---

## Contenido

```
software_limpio/
├── teoria/           # Fundamentos de diseño limpio
├── metricas/         # Catálogo de métricas de calidad
├── agentes/          # Agentes de control de calidad (CodeGuard, DesignReviewer, ArchitectAnalyst)
└── ejemplos/         # Código de ejemplo con métricas aplicadas
```

## Fundamentos

Seis principios universales de diseño (paradigma-agnósticos):

1. **Cohesión** - Elementos relacionados juntos
2. **Acoplamiento** - Minimizar dependencias entre módulos
3. **Ocultamiento de información** - Exponer solo lo necesario
4. **Modularidad** - Dividir en partes manejables
5. **Abstracción** - Separar qué hace de cómo lo hace
6. **Separación de responsabilidades** - Una razón para cambiar

## Métricas

| Contexto | Métricas Core | Ejemplo |
|----------|---------------|---------|
| Código | 15 | CC ≤ 10, LOC/función ≤ 20 |
| Diseño | 20 | CBO ≤ 5, LCOM ≤ 1, MI > 20 |
| Arquitectura | 20 | D ≈ 0, Layer Violations = 0 |

## Agentes de Calidad

| Agente | Momento | Duración | Acción | Estado |
|--------|---------|----------|--------|--------|
| **CodeGuard** | Pre-commit | < 5s | Advierte (no bloquea) | ✅ **v0.1.0** |
| **DesignReviewer** | Review/PR | 2-5 min | Bloquea si crítico | ✅ **v0.2.0** |
| **ArchitectAnalyst** | Fin de sprint | 10-30 min | Analiza tendencias | 🚧 Próximamente |

### CodeGuard (Agente de Código)

Sistema modular con 6 checks independientes:
- **PEP8Check** - Estilo de código (flake8)
- **SecurityCheck** - Vulnerabilidades (bandit)
- **ComplexityCheck** - Complejidad ciclomática (radon)
- **PylintCheck** - Calidad general
- **TypeCheck** - Tipos (mypy)
- **ImportCheck** - Imports sin usar

**Features:**
- ✅ Orquestación contextual (pre-commit, PR-review, full)
- ✅ Rich formatter profesional
- ✅ Configuración vía pyproject.toml (PEP 518)
- ✅ Integración con pre-commit framework

📖 **[Guía de Usuario CodeGuard](docs/guias/codeguard.md)**

---

### DesignReviewer (Agente de Diseño)

12 analyzers AST que detectan problemas de diseño en el delta de un PR. Puede **bloquear el merge** si detecta violaciones críticas.

```bash
# Analizar archivos del PR
designreviewer src/

# Salida JSON para CI/CD
designreviewer src/ --format json
```

**Analyzers implementados:**
- **Acoplamiento:** CBOAnalyzer, FanOutAnalyzer, CircularImportsAnalyzer
- **Cohesión y herencia:** LCOMAnalyzer, WMCAnalyzer, DITAnalyzer, NOPAnalyzer
- **Code Smells + SOLID:** GodObject, LongMethod, LongParameterList, FeatureEnvy, DataClumps

**Features:**
- ✅ 12 analyzers AST puro (+ radon para WMC)
- ✅ Separación visual BLOCKING ISSUES vs. Advertencias
- ✅ `estimated_effort` en horas por violación
- ✅ Exit code 1 si CRITICAL, 0 si no
- ✅ Salida Rich y JSON estructurado
- ✅ Configuración vía `[tool.designreviewer]` en pyproject.toml

📖 **[Guía de Usuario DesignReviewer](docs/guias/designreviewer.md)**

## Herramientas Base

- `radon` - Complejidad y mantenibilidad
- `pylint` - Análisis estático
- `bandit` - Seguridad
- `pydeps` - Dependencias
- `coverage.py` - Cobertura de tests

## Estado del Proyecto

### Implementación

| Componente | Estado | Progreso |
|------------|--------|----------|
| **Teoría y Fundamentos** | ✅ Completo | 100% |
| **CodeGuard (Agente de Código)** | ✅ v0.1.0 | 100% |
| **DesignReviewer (Agente de Diseño)** | ✅ v0.2.0 | 100% |
| **ArchitectAnalyst (Agente de Arquitectura)** | 🚧 Próximamente | 0% |

### CodeGuard - Roadmap

- [x] **Fase 1:** Configuración moderna (pyproject.toml)
- [x] **Fase 1.5:** Fundamentos arquitectura modular
- [x] **Fase 2:** 6 checks modulares implementados
- [x] **Fase 2.5:** Orquestación contextual
- [x] **Fase 4:** Output profesional con Rich
- [x] **Fase 5:** Integración pre-commit framework
- [x] **Fase 6:** Documentación completa
- [ ] **Fase 3:** IA opcional con Claude (suspendida temporalmente)

**Tests:** 517/517 pasando (100%)

### Próximos Pasos

1. ~~Release v0.1.0~~ ✅ Publicada
2. ~~Implementar DesignReviewer (v0.2.0)~~ ✅ Publicada
3. Implementar ArchitectAnalyst (v0.3.0)

## Autor

Víctor Valotto - FIUNER

## Licencia

MIT
