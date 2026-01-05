# Métricas de Calidad - Contexto: Código

**Nivel**: Función / Método

---

## Tamaño

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| LOC por función | ≤ 20 líneas | radon | Fundamental |
| SLOC por función | ≤ 15 líneas | radon | Sin comentarios |
| LLOC por función | ≤ 10 sentencias | radon | Lógicas ejecutables |

---

## Complejidad

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| CC (Cyclomatic) | ≤ 10 | radon, mccabe | **Fundamental** |
| Cognitive Complexity | ≤ 15 | SonarQube | Mejor para comprensión humana |
| Nesting Depth | ≤ 4 niveles | pylint | Indicador crítico |

---

## Estilo y Convenciones (Python)

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| PEP8 Violations | 0 | flake8 | **Fundamental** |
| Naming Conventions | 0 | pylint | Legibilidad |
| Type Errors | 0 | mypy | Si usa type hints |
| Pylint Score | ≥ 8.0 | pylint | Agregado de calidad |

---

## Documentación

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| Docstring Coverage | 100% público | interrogate | **Fundamental** |
| Missing Docstrings | 0 público | pydocstyle | API pública |

---

## Confiabilidad

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| Bare Excepts | 0 | pylint, bandit | Mal manejo de errores |
| Dead Code | 0 | vulture | Limpieza |
| Unused Variables | 0 | pylint | Código muerto |
| Unused Imports | 0 | autoflake | Limpieza |

---

## Seguridad

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| Insecure Functions | 0 | bandit | eval(), exec() |
| Hardcoded Secrets | 0 | detect-secrets | **Crítico** |
| SQL Injection Risk | 0 | bandit | Si aplica |

---

## Core Recomendado (15 métricas)

1. LOC por función (≤ 20)
2. CC (≤ 10)
3. Cognitive Complexity (≤ 15)
4. Nesting Depth (≤ 4)
5. PEP8 Violations (0)
6. Naming Conventions (0)
7. Pylint Score (≥ 8.0)
8. Docstring Coverage (100% público)
9. Bare Excepts (0)
10. Dead Code (0)
11. Unused Variables (0)
12. Insecure Functions (0)
13. Hardcoded Secrets (0)
14. Unused Imports (0)
15. Type Errors (0, si usa hints)

---

## Métricas Innecesarias

- Halstead completo (excepto V para MI)
- Essential Complexity (sin herramienta)
- Blank Lines (sin valor)
- Comment Ratio (subjetivo)
