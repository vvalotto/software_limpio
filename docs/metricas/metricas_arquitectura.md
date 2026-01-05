# MÉTRICAS DE CALIDAD - CONTEXTO: ARQUITECTURA
**Nivel: Paquete/Componente/Sistema**

## CATEGORÍA: MÉTRICAS DE ROBERT C. MARTIN (PAQUETES)

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Ca (Afferent Coupling) | Intermedio | Esencial | Contexto | pydeps, custom | Paquetes que dependen de este |
| Ce (Efferent Coupling) | Intermedio | Esencial | Contexto | pydeps, custom | Paquetes de los que este depende |
| I (Instability) | Intermedio | Esencial | Contexto | custom | Ce/(Ca+Ce), 0=estable, 1=inestable |
| A (Abstractness) | Avanzado | Esencial | Contexto | custom | Ratio clases abstractas (Na/Nc) |
| D (Distance) | Avanzado | Esencial | ≈ 0 | custom | \|A + I - 1\| distancia a secuencia principal |
| D' (Normalized Distance) | Avanzado | Complementaria | ≈ 0 | custom | D/√2, versión normalizada |

## CATEGORÍA: DEPENDENCIAS A NIVEL SISTEMA

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Total Dependencies | Básico | Esencial | ≤ 30 | pip, pipdeptree | Directas + transitivas |
| Direct Dependencies | Básico | Esencial | ≤ 15 | pip, requirements.txt | Dependencias explícitas |
| Transitive Dependencies | Intermedio | Complementaria | - | pipdeptree | Dependencias de dependencias |
| Outdated Dependencies | Básico | Esencial | 0 | pip-review, safety | Seguridad y mantenibilidad |
| Dependency Depth | Intermedio | Complementaria | ≤ 5 | pipdeptree | Profundidad del árbol |
| External Dependencies | Básico | Complementaria | ≤ 15 | pipdeptree | Paquetes externos (PyPI) |
| Dependency Cycles | Básico | Esencial | 0 | pydeps, import-linter | Ciclos entre paquetes |

## CATEGORÍA: ARQUITECTURA LIMPIA (CLEAN ARCHITECTURE)

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Layer Violations | Intermedio | Esencial | 0 | import-linter | Deps que cruzan capas incorrectamente |
| Inward Dependencies | Intermedio | Esencial | 100% | pydeps | Dependencias hacia el centro OK |
| Outward Dependencies | Intermedio | Esencial | 0 | pydeps | Dependencias hacia afuera - violaciones |
| Domain Purity | Avanzado | Esencial | 100% | custom | % dominio sin deps externas |
| Use Case Count | Básico | Complementaria | - | manual/ast | Cantidad de casos de uso |
| Entity Count | Básico | Complementaria | - | manual/ast | Cantidad de entidades de dominio |
| Adapter Count | Intermedio | Complementaria | - | manual/ast | Cantidad de adaptadores |

## CATEGORÍA: DSM (DESIGN STRUCTURE MATRIX)

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Cyclic Dependencies (DSM) | Avanzado | Esencial | 0 | pydeps | Dependencias bajo la diagonal |
| Layering Violations (DSM) | Avanzado | Esencial | 0 | import-linter | Deps que rompen capas |
| Matrix Density | Avanzado | Complementaria | < 20% | custom | % de celdas ocupadas |
| Propagation Cost | Avanzado | Complementaria | - | custom | **ACADÉMICA** - costo de propagación |
| Cluster Count | Avanzado | Complementaria | - | custom | **SIN HERRAMIENTA** - clusters en DSM |
| Bandwidth | Avanzado | Complementaria | - | custom | **ACADÉMICA** - distancia de diagonal |
| Dependency Matrix | Avanzado | Complementaria | - | pydeps + script | **REPRESENTACIÓN** - no métrica |

## CATEGORÍA: SEGURIDAD A NIVEL SISTEMA

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Vulnerabilities | Básico | Esencial | 0 | bandit, safety | Vulnerabilidades conocidas |
| Security Rating | Básico | Esencial | A | SonarQube | Agregado A-B-C-D-E |
| Security Hotspots | Intermedio | Esencial | 0 | SonarQube, bandit | Código que requiere revisión |
| Dependency Vulnerabilities | Básico | Esencial | 0 CVE | safety, pip-audit | CVEs en dependencias |

## CATEGORÍA: TAMAÑO Y ESTRUCTURA DEL SISTEMA

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Total LOC | Básico | Complementaria | - | cloc, radon | Tamaño total del sistema |
| Files Count | Básico | Complementaria | - | cloc, wc | Cantidad de archivos |
| Modules Count | Básico | Complementaria | ≤ 50 | pydeps | Cantidad de módulos |
| Packages Count | Intermedio | Complementaria | ≤ 10 | pydeps | Cantidad de paquetes |
| Average Module Size | Básico | Complementaria | ≤ 500 LOC | radon | Ya cubierto en Diseño |

## CATEGORÍA: TESTING A NIVEL SISTEMA

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Total Line Coverage | Básico | Esencial | > 80% | coverage.py | Cobertura global del proyecto |
| Total Branch Coverage | Intermedio | Esencial | > 75% | coverage.py | Cobertura de ramas global |
| Tests Passed/Failed | Básico | Esencial | 100% pass | pytest | Estado de la suite de tests |
| Test Execution Time | Intermedio | Complementaria | < 5 min | pytest | Tiempo total de ejecución |

## CATEGORÍA: MANTENIBILIDAD A NIVEL SISTEMA

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Average MI (sistema) | Intermedio | Esencial | > 20 | radon | MI promedio del proyecto |
| Technical Debt (total) | Avanzado | Complementaria | - | SonarQube | Tiempo total para corregir |
| Technical Debt Ratio | Avanzado | Esencial | < 5% | SonarQube | Deuda / esfuerzo desarrollo |
| Total Code Smells | Intermedio | Esencial | < 100 | SonarQube, pylint | Problemas de diseño totales |
| Total Bugs | Básico | Esencial | 0 | SonarQube, pylint | Defectos potenciales totales |

## CATEGORÍA: DUPLICACIÓN A NIVEL SISTEMA

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Total Duplicated Lines | Básico | Esencial | < 3% | SonarQube, jscpd | Duplicación total del proyecto |
| Total Duplicated Blocks | Básico | Complementaria | - | SonarQube, jscpd | Redundante con Lines |

## CATEGORÍA: COMPLEJIDAD A NIVEL SISTEMA

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Average CC (sistema) | Básico | Esencial | ≤ 5 | radon | CC promedio del proyecto |
| Max CC (sistema) | Básico | Esencial | ≤ 10 | radon | CC máximo encontrado |
| Total CC | Intermedio | Complementaria | - | radon | **SIN UMBRAL** - depende de tamaño |
| CC Distribution | Intermedio | Esencial | 80% A-B | radon | Distribución por rangos |

---

## RESUMEN CUANTITATIVO

### Por Utilidad
- **Esenciales:** 31 métricas
- **Complementarias útiles:** 16 métricas
- **Innecesarias/sin fundamento:** 7 métricas

### Métricas INNECESARIAS o SIN FUNDAMENTO

**DSM (académicas/sin herramienta):**
1. **Propagation Cost** - académica, difícil de calcular
2. **Cluster Count** - sin herramienta práctica
3. **Bandwidth** - académica, poco valor
4. **Dependency Matrix** - representación, no métrica

**DUPLICACIÓN (redundante):**
5. **Total Duplicated Blocks** - redundante con Duplicated Lines

**TAMAÑO (redundante):**
6. **Total LOC** - no es indicador de calidad
7. **Total CC** - sin umbral, depende del tamaño

### CORE RECOMENDADO (20 métricas esenciales)

**Principios de Martin (6):**
1. Ca (Afferent Coupling)
2. Ce (Efferent Coupling)
3. I (Instability)
4. A (Abstractness)
5. D (Distance) ≈ 0
6. Technical Debt Ratio < 5%

**Dependencias (4):**
7. Total Dependencies ≤ 30
8. Direct Dependencies ≤ 15
9. Outdated Dependencies = 0
10. Dependency Cycles = 0

**Clean Architecture (4):**
11. Layer Violations = 0
12. Inward Dependencies = 100%
13. Outward Dependencies = 0
14. Domain Purity = 100%

**Seguridad (3):**
15. Vulnerabilities = 0
16. Security Rating = A
17. Dependency Vulnerabilities = 0 CVE

**Testing Global (2):**
18. Total Line Coverage > 80%
19. Tests Passed = 100%

**Calidad Global (3):**
20. Average MI > 20
21. Average CC ≤ 5
22. Total Duplicated Lines < 3%

---

## NOTAS IMPORTANTES

### Sobre Métricas de Robert C. Martin:
- **La métrica D (Distance) es la más importante** - indica desviación de la secuencia principal
- **Zonas problemáticas:**
  - **Zona de Dolor** (A≈0, I≈0): Paquetes concretos y estables - difíciles de cambiar
  - **Zona de Inutilidad** (A≈1, I≈1): Paquetes abstractos e inestables - nadie los usa
- **Los valores dependen del contexto:**
  - Paquetes de dominio: I bajo, A alto
  - Paquetes de infraestructura: I alto, A bajo
  - Paquetes intermedios: cerca de la línea A + I = 1

### Sobre Clean Architecture:
- **Layer Violations = 0 es no negociable**
- Las dependencias siempre deben apuntar hacia adentro
- El dominio debe ser puro (Domain Purity = 100%)
- Use Case Count, Entity Count, Adapter Count son útiles para monitorear pero no tienen umbrales

### Sobre DSM:
- **Solo usar para proyectos grandes** (>20 módulos)
- Cyclic Dependencies detecta problemas arquitectónicos
- La mayoría de métricas DSM son académicas sin valor práctico
- La matriz es una representación visual, no una métrica

### Sobre Dependencias:
- **Outdated Dependencies = 0 es crítico para seguridad**
- Total Dependencies incluye transitivas - crece rápido
- Direct Dependencies debe mantenerse bajo para facilitar upgrades
- Dependency Cycles indican problemas de diseño serios

### Sobre Seguridad:
- **CVEs deben ser 0**
- Security Hotspots requieren revisión manual
- Usar safety + pip-audit + bandit en CI/CD

### Herramientas Clave:
1. **pydeps**: Visualización y análisis de dependencias
2. **import-linter**: Enforcement de reglas arquitectónicas
3. **SonarQube**: Dashboard completo de calidad
4. **safety/pip-audit**: Vulnerabilidades en dependencias
5. **coverage.py**: Cobertura agregada

### Frecuencia de Medición:
- **En cada commit**: Tests, vulnerabilities, layer violations
- **Diario/CI**: Coverage, code smells, bugs
- **Semanal**: Outdated dependencies, technical debt
- **Mensual**: Métricas de Martin (Ca, Ce, I, A, D)

### Contexto de Aplicación:
Estas métricas se miden **a nivel de paquete/componente o sistema completo**, no a nivel de función o clase individual.
