# Catálogo de Métricas Clasificado

Ingeniería de Software - Calidad de Diseño

## Clasificación

- **Nivel**: Básico / Intermedio / Avanzado
- **Contexto**: Código / Diseño / Arquitectura
- **Utilidad**: Esencial / Complementaria

---

## 1. Métricas de Tamaño

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta |
|---------|-------|----------|----------|--------|-------------|
| LOC (Lines of Code) | Básico | Código | Esencial | < 500/módulo | radon, cloc |
| SLOC (Source LOC) | Básico | Código | Esencial | - | radon, cloc |
| Average Module Size | Intermedio | Diseño | Esencial | < 500 LOC | radon |
| Average Class Size | Intermedio | Diseño | Esencial | < 300 LOC | radon |
| Average Method Size | Básico | Código | Esencial | < 50 LOC | radon |

---

## 2. Métricas de Complejidad

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta |
|---------|-------|----------|----------|--------|-------------|
| CC (Cyclomatic Complexity) | Básico | Código | **Esencial** | ≤ 10 | radon, pylint |
| Cognitive Complexity | Intermedio | Código | Esencial | ≤ 15 | SonarQube |
| Average CC | Intermedio | Diseño | Esencial | ≤ 5 | radon |
| Max CC | Básico | Código | Esencial | ≤ 10 | radon |
| Nesting Depth | Básico | Código | Esencial | ≤ 4 | pylint |

---

## 3. Métricas de Halstead

| Métrica | Nivel | Utilidad | Observación |
|---------|-------|----------|-------------|
| Volumen (V) | Avanzado | Complementaria | Solo para cálculo de MI |
| Resto | Avanzado | **Innecesaria** | Académicas, poco valor práctico |

**Recomendación**: Descartar Halstead excepto Volumen (usado en MI).

---

## 4. Métricas de Mantenibilidad

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta |
|---------|-------|----------|----------|--------|-------------|
| Maintainability Index (MI) | Intermedio | Diseño | **Esencial** | > 20 | radon, SonarQube |
| Technical Debt Ratio | Avanzado | Diseño | Esencial | < 5% | SonarQube |
| Code Smells | Intermedio | Diseño | Esencial | 0 | SonarQube, pylint |

---

## 5. Métricas de Cohesión

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta |
|---------|-------|----------|----------|--------|-------------|
| LCOM (Lack of Cohesion) | Intermedio | Diseño | **Esencial** | ≤ 1 | pylint |
| LCOM1-5 | Avanzado | Diseño | **Innecesaria** | - | Redundantes |

**Recomendación**: Usar solo LCOM estándar.

---

## 6. Métricas de Acoplamiento

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta |
|---------|-------|----------|----------|--------|-------------|
| CBO (Coupling Between Objects) | Intermedio | Diseño | **Esencial** | ≤ 5 | pylint, SonarQube |
| Fan-In | Intermedio | Diseño | Complementaria | - | pydeps |
| Fan-Out | Intermedio | Diseño | Esencial | ≤ 7 | pydeps |
| Dependency Cycles | Intermedio | Arquitectura | **Esencial** | 0 | pydeps |

---

## 7. Métricas de Robert C. Martin (Paquetes)

| Métrica | Nivel | Utilidad | Umbral | Fórmula |
|---------|-------|----------|--------|---------|
| Ca (Afferent Coupling) | Avanzado | Esencial | Contexto | Paquetes que dependen de este |
| Ce (Efferent Coupling) | Avanzado | Esencial | Contexto | Paquetes de los que depende |
| I (Instability) | Avanzado | Esencial | 0-1 | Ce/(Ca+Ce) |
| A (Abstractness) | Avanzado | Complementaria | 0-1 | Clases abstractas/Total |
| D (Distance) | Avanzado | **Esencial** | ≈ 0 | \|A + I - 1\| |

**Recomendación**: Conjunto muy útil para arquitectura avanzada.

---

## 8. Métricas CK (Chidamber-Kemerer)

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta |
|---------|-------|----------|----------|--------|-------------|
| WMC (Weighted Methods per Class) | Intermedio | Diseño | Esencial | ≤ 20 | radon |
| DIT (Depth of Inheritance Tree) | Intermedio | Diseño | Esencial | ≤ 5 | pylint |
| NOC (Number of Children) | Intermedio | Diseño | Complementaria | - | pylint |

---

## 9. Métricas de Duplicación

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta |
|---------|-------|----------|----------|--------|-------------|
| Duplicated Lines | Básico | Código | **Esencial** | < 3% | SonarQube, jscpd |
| Duplicated Blocks | Básico | Código | Esencial | 0 | SonarQube |

---

## 10. Métricas de Testing

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta |
|---------|-------|----------|----------|--------|-------------|
| Line Coverage | Básico | Código | **Esencial** | > 80% | coverage.py |
| Branch Coverage | Intermedio | Código | Esencial | > 75% | coverage.py |
| Tests Passed/Failed | Básico | Código | Esencial | 100% pass | pytest |
| Mutation Score | Avanzado | Código | Complementaria | > 70% | mutmut |

---

## 11. Métricas de Seguridad

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta |
|---------|-------|----------|----------|--------|-------------|
| Vulnerabilities | Intermedio | Código | **Esencial** | 0 | bandit, safety |
| Hardcoded Secrets | Básico | Código | Esencial | 0 | detect-secrets |
| Insecure Functions | Básico | Código | Esencial | 0 | bandit |
| Dependency CVEs | Básico | Arquitectura | Esencial | 0 | pip-audit |

---

## 12. Métricas de Estilo (Python)

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta |
|---------|-------|----------|----------|--------|-------------|
| PEP8 Violations | Básico | Código | **Esencial** | 0 | flake8 |
| Naming Conventions | Básico | Código | Esencial | 0 | pylint |
| Type Hints Coverage | Intermedio | Código | Esencial | > 80% | mypy |
| Pylint Score | Básico | Código | **Esencial** | > 8.0 | pylint |

---

## 13. Métricas de Arquitectura Limpia

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta |
|---------|-------|----------|----------|--------|-------------|
| Layer Violations | Avanzado | Arquitectura | **Esencial** | 0 | import-linter |
| Domain Purity | Avanzado | Arquitectura | Esencial | 100% | custom |
| Inward Dependencies | Avanzado | Arquitectura | Esencial | 100% | pydeps |

---

## Resumen Ejecutivo

### Core Recomendado: 35 Métricas

**Básico (15)**:
1. LOC, SLOC
2. Cyclomatic Complexity (CC)
3. Nesting Depth
4. Maintainability Index (MI)
5. Duplicated Lines
6. Line Coverage
7. PEP8 Violations
8. Pylint Score
9. Hardcoded Secrets
10. Insecure Functions
11. Bare Excepts

**Intermedio (12)**:
12. Cognitive Complexity
13. Average CC
14. Code Smells
15. CBO (Coupling)
16. Fan-Out
17. LCOM
18. WMC, DIT
19. Branch Coverage
20. Dependency Cycles

**Avanzado (8)**:
21. Métricas de Martin (Ca, Ce, I, D)
22. Domain Purity
23. Layer Violations
24. Technical Debt Ratio

### Métricas Innecesarias (~40)

- Halstead completo (excepto V)
- LCOM variantes (2-5)
- DSM completas
- Métricas sin herramienta disponible
