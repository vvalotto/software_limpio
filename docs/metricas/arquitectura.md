# Métricas de Calidad - Contexto: Arquitectura

**Nivel**: Paquete / Componente / Sistema

---

## Métricas de Robert C. Martin (Paquetes)

| Métrica | Umbral | Fórmula | Observación |
|---------|--------|---------|-------------|
| Ca (Afferent Coupling) | contexto | Paquetes que dependen de este | Responsabilidad |
| Ce (Efferent Coupling) | contexto | Paquetes de los que depende | Dependencia |
| I (Instability) | 0-1 | Ce/(Ca+Ce) | 0=estable, 1=inestable |
| A (Abstractness) | 0-1 | Na/Nc | Ratio abstractas |
| D (Distance) | ≈ 0 | \|A + I - 1\| | **Clave** |

**Zonas problemáticas**:
- **Zona de Dolor** (A≈0, I≈0): Concreto y estable → difícil cambiar
- **Zona de Inutilidad** (A≈1, I≈1): Abstracto e inestable → nadie lo usa

---

## Dependencias a Nivel Sistema

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| Total Dependencies | ≤ 30 | pipdeptree | Directas + transitivas |
| Direct Dependencies | ≤ 15 | pip | Explícitas |
| Outdated Dependencies | 0 | pip-review | **Seguridad** |
| Dependency Cycles | 0 | pydeps | **Crítico** |

---

## Arquitectura Limpia

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| Layer Violations | 0 | import-linter | **No negociable** |
| Inward Dependencies | 100% | pydeps | Hacia el centro |
| Outward Dependencies | 0 | pydeps | Violaciones |
| Domain Purity | 100% | custom | Sin deps externas |

---

## Seguridad a Nivel Sistema

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| Vulnerabilities | 0 | bandit, safety | Conocidas |
| Security Rating | A | SonarQube | Agregado |
| Dependency CVEs | 0 | pip-audit, safety | **Crítico** |

---

## Testing a Nivel Sistema

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| Total Line Coverage | > 80% | coverage.py | Global |
| Total Branch Coverage | > 75% | coverage.py | Global |
| Tests Passed | 100% | pytest | Estado de suite |

---

## Calidad Global

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| Average MI | > 20 | radon | Promedio proyecto |
| Average CC | ≤ 5 | radon | Promedio proyecto |
| Max CC | ≤ 10 | radon | Hotspots |
| Total Duplicated Lines | < 3% | SonarQube | Global |
| Technical Debt Ratio | < 5% | SonarQube | Deuda total |
| Total Bugs | 0 | SonarQube | Defectos |

---

## Core Recomendado (20 métricas)

**Principios de Martin (5)**:
1. Ca (Afferent Coupling)
2. Ce (Efferent Coupling)
3. I (Instability)
4. A (Abstractness)
5. D (Distance) ≈ 0

**Dependencias (4)**:
6. Total Dependencies ≤ 30
7. Direct Dependencies ≤ 15
8. Outdated Dependencies = 0
9. Dependency Cycles = 0

**Clean Architecture (4)**:
10. Layer Violations = 0
11. Inward Dependencies = 100%
12. Outward Dependencies = 0
13. Domain Purity = 100%

**Seguridad (3)**:
14. Vulnerabilities = 0
15. Security Rating = A
16. Dependency CVEs = 0

**Testing (2)**:
17. Total Line Coverage > 80%
18. Tests Passed = 100%

**Calidad (2)**:
19. Average MI > 20
20. Average CC ≤ 5

---

## Frecuencia de Medición

| Frecuencia | Métricas |
|------------|----------|
| Cada commit | Tests, vulnerabilities, layer violations |
| Diario/CI | Coverage, code smells, bugs |
| Semanal | Outdated dependencies, technical debt |
| Mensual | Métricas de Martin (Ca, Ce, I, A, D) |

---

## Herramientas Clave

1. **pydeps**: Visualización y análisis de dependencias
2. **import-linter**: Enforcement de reglas arquitectónicas
3. **SonarQube**: Dashboard completo
4. **safety/pip-audit**: Vulnerabilidades en dependencias
5. **coverage.py**: Cobertura agregada

---

## Métricas Innecesarias

- DSM completo (Propagation Cost, Cluster Count, Bandwidth)
- Total LOC (no es indicador de calidad)
- Total CC (sin umbral, depende del tamaño)
- Matrix Density (académica)
