# Software Limpio

Framework Python para control de calidad automatizado en tres niveles, inspirado en la trilogía de Robert C. Martin. Transforma al profesional de software de "escritor de código" a **director y evaluador de calidad**, usando métricas como herramientas objetivas de verificación.

---

## Agentes de Calidad

| Agente | Momento | Duración | Acción | Versión |
|--------|---------|----------|--------|---------|
| **CodeGuard** | Pre-commit | < 5s | Advierte, no bloquea | ✅ v0.1.0 |
| **DesignReviewer** | PR Review | 2-5 min | **Bloquea si hay CRITICAL** | ✅ v0.2.0 |
| **ArchitectAnalyst** | Fin de sprint | 10-30 min | Informa tendencias, no bloquea | ✅ v0.3.0 |

---

## Instalación

```bash
git clone https://github.com/vvalotto/software_limpio.git
cd software_limpio
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

---

## Uso Rápido

### CodeGuard — análisis pre-commit

```bash
codeguard src/
codeguard src/ --format json
```

Nunca bloquea. Integración con pre-commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.3.0
    hooks:
      - id: codeguard
        args: ['--analysis-type', 'pre-commit']
```

### DesignReviewer — guardián de calidad de diseño en PRs

```bash
designreviewer src/
designreviewer src/ --format json
```

Exit code 1 si hay violaciones CRITICAL (bloquea el merge en CI). Exit code 0 si no.

### ArchitectAnalyst — salud arquitectónica del sprint

```bash
architectanalyst src/ --sprint-id sprint-12
architectanalyst src/ --sprint-id sprint-12 --format json
```

Siempre exit code 0. Persiste snapshots en SQLite y muestra tendencias ↑↓= entre sprints.

---

## Descripción de los Agentes

### CodeGuard

6 checks modulares sobre cada archivo Python del changeset:

- **PEP8Check** — estilo de código (flake8)
- **SecurityCheck** — vulnerabilidades (bandit)
- **ComplexityCheck** — complejidad ciclomática (radon)
- **PylintCheck** — calidad general
- **TypeCheck** — tipos estáticos (mypy)
- **ImportCheck** — imports sin usar

📖 [Guía de Usuario](docs/guias/codeguard.md) · [Guía de Adopción](docs/guias/adopcion-codeguard.md)

---

### DesignReviewer

12 analyzers AST que detectan problemas de diseño:

- **Acoplamiento:** CBO, Fan-Out, Importaciones Circulares
- **Cohesión y herencia:** LCOM, WMC, DIT, NOP
- **Code Smells + SOLID:** God Object, Long Method, Long Parameter List, Feature Envy, Data Clumps

Configuración en `pyproject.toml`:

```toml
[tool.designreviewer]
max_cbo = 5
max_wmc = 20
max_dit = 5
```

📖 [Guía de Usuario](docs/guias/designreviewer.md) · [Guía de Adopción](docs/guias/adopcion-designreviewer.md)

---

### ArchitectAnalyst

7 métricas cross-module sobre la arquitectura completa:

- **Métricas de Martin:** Ca, Ce, I (inestabilidad), A (abstracción), D (distancia al Main Sequence)
- **Estructurales:** Ciclos de dependencias (algoritmo de Tarjan), Violaciones de capas

Configuración en `pyproject.toml`:

```toml
[tool.architectanalyst]
max_instability = 0.8
max_distance_critical = 0.5

[tool.architectanalyst.layers]
domain = []
application = ["domain"]
infrastructure = ["application", "domain"]
```

📖 [Guía de Usuario](docs/guias/architectanalyst.md) · [Guía de Adopción](docs/guias/adopcion-architectanalyst.md)

---

## Estructura del Proyecto

```
software_limpio/
├── src/quality_agents/      # Código fuente de los tres agentes
│   ├── codeguard/
│   ├── designreviewer/
│   ├── architectanalyst/
│   └── shared/              # Verifiable, QualityConfig, reporting
├── docs/                    # Documentación
│   ├── guias/               # Guías de usuario y adopción
│   ├── agentes/             # Especificación técnica
│   ├── metricas/            # Catálogo de métricas
│   └── teoria/              # Fundamentos de diseño
├── tests/                   # Unit, integration, e2e
├── gestion/                 # Backlog y releases
└── configs/                 # Configuraciones de ejemplo
```

---

## Documentación

- [Guías de Usuario](docs/guias/README.md)
- [Especificación Técnica de Agentes](docs/agentes/especificacion_agentes_calidad.md)
- [Catálogo de Métricas](docs/metricas/Metricas_Clasificadas.md)

---

## Autor

Víctor Valotto — FIUNER

## Licencia

MIT
