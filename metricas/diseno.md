# Métricas de Calidad - Contexto: Diseño

**Nivel**: Clase / Módulo

---

## Tamaño y Complejidad

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| Average Class Size | ≤ 200 LOC | radon | Clases grandes = problemas |
| Average Module Size | ≤ 500 LOC | radon | Módulos grandes = problemas |
| WMC (Weighted Methods) | ≤ 20 | radon | Suma de CC de métodos |
| Total CC por clase | ≤ 30 | radon | Complejidad agregada |

---

## Cohesión

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| LCOM | ≤ 1 | pylint | **Usar solo esta variante** |

**Nota**: LCOM1-5 son variantes redundantes. Usar solo LCOM estándar.

---

## Acoplamiento

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| CBO (Coupling Between Objects) | ≤ 5 | pylint, SonarQube | **Clave** |
| Fan-In | contexto | pydeps | Reusabilidad |
| Fan-Out | ≤ 7 | pydeps | Dependencias |
| Imports Count | ≤ 10 | pylint | Por módulo |

---

## Herencia

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| DIT (Depth of Inheritance) | ≤ 5 | pylint | **Crítico** |
| NOP (Number of Parents) | ≤ 1 | ast | Herencia múltiple |
| NOC (Number of Children) | contexto | ast | Hijos directos |

**Nota**: SIX, AIF, MIF, PF son académicas sin adopción práctica.

---

## Mantenibilidad

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| Maintainability Index (MI) | > 20 | radon | **Métrica rey** |
| Technical Debt Ratio | < 5% | SonarQube | Deuda/esfuerzo |
| Code Smells | 0 críticos | SonarQube | Problemas de diseño |

---

## Duplicación

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| Duplicated Lines | < 3% | SonarQube, jscpd | **Umbral industria** |
| Duplicated Blocks | 0 | SonarQube | Bloques repetidos |

---

## Testing

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| Line Coverage | > 80% | coverage.py | **Mínimo aceptable** |
| Branch Coverage | > 75% | coverage.py | Más exigente |

**Nota**: Function/Class Coverage son redundantes con Line Coverage.

---

## Documentación

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| README Presence | Sí | - | Entrada al módulo |
| Public API Documented | 100% | interrogate | APIs públicas |

---

## Dependencias

| Métrica | Umbral | Herramienta | Observación |
|---------|--------|-------------|-------------|
| Circular Imports | 0 | pylint, import-linter | **Crítico** |
| Bugs | 0 | SonarQube | Defectos potenciales |

---

## Core Recomendado (20 métricas)

**Tamaño (4)**:
1. Average Class Size (≤ 200)
2. Average Module Size (≤ 500)
3. WMC (≤ 20)
4. Total CC por clase (≤ 30)

**Cohesión y Acoplamiento (4)**:
5. LCOM (≤ 1)
6. CBO (≤ 5)
7. Fan-In (contexto)
8. Fan-Out (≤ 7)

**Herencia (2)**:
9. DIT (≤ 5)
10. NOP (≤ 1)

**Mantenibilidad (3)**:
11. MI (> 20)
12. Technical Debt Ratio (< 5%)
13. Code Smells (0 críticos)

**Duplicación (2)**:
14. Duplicated Lines (< 3%)
15. Duplicated Blocks (0)

**Testing (2)**:
16. Line Coverage (> 80%)
17. Branch Coverage (> 75%)

**Documentación y Confiabilidad (3)**:
18. README Presence (Sí)
19. Public API Documented (100%)
20. Circular Imports (0)

---

## Métricas Innecesarias

- LCOM variantes (2-5)
- TCC, LCC (sin herramienta)
- RFC (sin herramienta clara)
- Function/Class/Statement Coverage (redundantes)
- SIX, AIF, MIF, PF (académicas)
