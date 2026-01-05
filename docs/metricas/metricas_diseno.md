# MÉTRICAS DE CALIDAD - CONTEXTO: DISEÑO
**Nivel: Clase/Módulo/Estructura de Diseño**

## CATEGORÍA: TAMAÑO Y COMPLEJIDAD DE CLASES/MÓDULOS

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Average Class Size | Básico | Esencial | ≤ 200 LOC | radon | Clases demasiado grandes |
| Average Module Size | Básico | Esencial | ≤ 500 LOC | radon | Módulos demasiado grandes |
| Functions Count por módulo | Básico | Complementaria | ≤ 20 | radon | Indicador de foco del módulo |
| Classes Count por módulo | Básico | Complementaria | ≤ 5 | radon | Exceso indica bajo cohesión |
| WMC (Weighted Methods per Class) | Intermedio | Esencial | ≤ 20 | radon, pylint | Suma de CC de métodos |
| Total CC por clase | Intermedio | Esencial | ≤ 30 | radon | Complejidad agregada de clase |
| Average CC por clase | Intermedio | Complementaria | ≤ 5 | radon | Complementa WMC |

## CATEGORÍA: COHESIÓN

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| LCOM (Lack of Cohesion) | Intermedio | Esencial | ≤ 1 | pylint, radon | Métodos que no comparten atributos |
| LCOM1 | Avanzado | Complementaria | - | custom | Variante original Henderson-Sellers |
| LCOM2 | Avanzado | Complementaria | - | custom | **INNECESARIA** - redundante con LCOM |
| LCOM3 | Avanzado | Complementaria | - | custom | **INNECESARIA** - redundante con LCOM |
| LCOM4 | Avanzado | Complementaria | - | custom | **INNECESARIA** - redundante con LCOM |
| LCOM5 | Avanzado | Complementaria | - | custom | **INNECESARIA** - redundante con LCOM |
| TCC (Tight Class Cohesion) | Avanzado | Complementaria | > 0.5 | custom | **SIN HERRAMIENTA** - difícil de medir |
| LCC (Loose Class Cohesion) | Avanzado | Complementaria | > 0.7 | custom | **SIN HERRAMIENTA** - difícil de medir |
| Cohesion Ratio | Intermedio | Complementaria | > 0.5 | custom | **SIN HERRAMIENTA** - alternativa a LCOM |

## CATEGORÍA: ACOPLAMIENTO (NIVEL CLASE/MÓDULO)

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| CBO (Coupling Between Objects) | Intermedio | Esencial | ≤ 5 | pylint, SonarQube | Clases acopladas a esta |
| Fan-In (módulo) | Intermedio | Esencial | - | pydeps, import-linter | Módulos que importan este |
| Fan-Out (módulo) | Intermedio | Esencial | ≤ 7 | pydeps, import-linter | Módulos importados por este |
| Imports Count | Básico | Complementaria | ≤ 10 | pylint | Cantidad de imports directos |
| RFC (Response for Class) | Avanzado | Complementaria | ≤ 50 | custom | **SIN HERRAMIENTA** - métodos ejecutables |
| Coupling Factor (CF) | Avanzado | Complementaria | - | custom | **ACADÉMICA** - poco práctica |

## CATEGORÍA: HERENCIA

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| DIT (Depth of Inheritance Tree) | Intermedio | Esencial | ≤ 5 | pylint, ast | Profundidad máxima de herencia |
| NOC (Number of Children) | Intermedio | Complementaria | ≤ 7 | ast | Cantidad de hijos directos |
| NOP (Number of Parents) | Intermedio | Esencial | ≤ 1 | ast | Herencia múltiple (Python) |
| Abstract Classes Count | Intermedio | Complementaria | - | ast | Indicador de abstracción |
| Interfaces Count | Intermedio | Complementaria | - | ast | Protocolos/ABCs en Python |
| SIX (Specialization Index) | Avanzado | Complementaria | - | custom | **ACADÉMICA** - poco usada |
| AIF (Attribute Inheritance Factor) | Avanzado | Complementaria | - | custom | **ACADÉMICA** - poco usada |
| MIF (Method Inheritance Factor) | Avanzado | Complementaria | - | custom | **ACADÉMICA** - poco usada |
| PF (Polymorphism Factor) | Avanzado | Complementaria | - | custom | **ACADÉMICA** - poco usada |

## CATEGORÍA: MANTENIBILIDAD

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Maintainability Index (MI) | Intermedio | Esencial | > 20 | radon, SonarQube | Índice compuesto 0-100 |
| MI sin comentarios | Intermedio | Complementaria | > 20 | radon | Variante sin peso de docs |
| Technical Debt | Avanzado | Complementaria | - | SonarQube | Tiempo para corregir issues |
| Technical Debt Ratio | Avanzado | Esencial | < 5% | SonarQube | Deuda / esfuerzo desarrollo |
| Code Smells | Intermedio | Esencial | 0 | SonarQube, pylint | Problemas de diseño/estilo |
| Maintainability Rating | Intermedio | Complementaria | A | SonarQube | Agregado A-B-C-D-E |

## CATEGORÍA: DUPLICACIÓN

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Duplicated Lines | Básico | Esencial | < 3% | SonarQube, pylint | Porcentaje de duplicación |
| Duplicated Blocks | Básico | Esencial | 0 | SonarQube, jscpd | Bloques de código repetido |
| Duplicated Files | Intermedio | Complementaria | 0 | SonarQube | Archivos con duplicación |
| Duplication Density | Básico | Complementaria | < 3% | SonarQube | Redundante con Duplicated Lines |
| Clone Classes | Avanzado | Complementaria | 0 | jscpd | Grupos de clones similares |
| Clone Coverage | Avanzado | Complementaria | < 5% | jscpd | % de código que es clon |

## CATEGORÍA: TESTING Y COBERTURA (NIVEL CLASE)

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Line Coverage | Básico | Esencial | > 80% | coverage.py, pytest-cov | Mínimo aceptable |
| Branch Coverage | Intermedio | Esencial | > 75% | coverage.py | Más exigente que líneas |
| Function Coverage | Básico | Complementaria | > 90% | coverage.py | Redundante con Line Coverage |
| Class Coverage | Básico | Complementaria | > 90% | coverage.py | Redundante con Line Coverage |
| Statement Coverage | Intermedio | Complementaria | > 80% | coverage.py | Similar a Line Coverage |
| Condition Coverage | Avanzado | Complementaria | > 70% | coverage.py | Para código crítico |
| MC/DC Coverage | Avanzado | Complementaria | > 80% | custom | **SOLO IEC 62304** - dispositivos médicos |
| Test Count | Básico | Complementaria | - | pytest | **SIN UMBRAL** - no es indicador |
| Test/Code Ratio | Intermedio | Complementaria | > 1:1 | custom | Líneas test / líneas código |
| Mutation Score | Avanzado | Complementaria | > 70% | mutmut, cosmic-ray | Calidad de tests, no cantidad |

## CATEGORÍA: DOCUMENTACIÓN (NIVEL MÓDULO)

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Comment Density (módulo) | Básico | Complementaria | 10-30% | radon | % comentarios / código |
| README Presence | Básico | Esencial | Sí | custom | Documentación de entrada |
| Documentation Ratio | Intermedio | Complementaria | > 0.2 | custom | Líneas doc / líneas código |
| Public API Documented | Básico | Esencial | 100% | interrogate | APIs públicas documentadas |

## CATEGORÍA: CONFIABILIDAD (NIVEL CLASE/MÓDULO)

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Bugs | Básico | Esencial | 0 | SonarQube, pylint | Defectos potenciales |
| Reliability Rating | Intermedio | Complementaria | A | SonarQube | Agregado A-B-C-D-E |

## CATEGORÍA: DEPENDENCIAS (NIVEL MÓDULO)

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Circular Imports | Básico | Esencial | 0 | pylint, import-linter | Problema de diseño crítico |
| Internal Dependencies | Intermedio | Complementaria | ≤ 5 | pydeps | Dependencias entre módulos propios |

---

## RESUMEN CUANTITATIVO

### Por Utilidad
- **Esenciales:** 26 métricas
- **Complementarias útiles:** 22 métricas
- **Innecesarias/sin fundamento:** 15 métricas

### Métricas INNECESARIAS o SIN FUNDAMENTO

**COHESIÓN (redundantes):**
1. LCOM2, LCOM3, LCOM4, LCOM5 - usar solo LCOM
2. TCC, LCC - sin herramienta práctica

**ACOPLAMIENTO (académicas):**
3. RFC - sin herramienta clara
4. Coupling Factor - académica

**HERENCIA (académicas):**
5. SIX, AIF, MIF, PF - poco usadas, sin herramientas

**TESTING (redundantes):**
6. Function Coverage, Class Coverage - redundantes con Line Coverage
7. Statement Coverage - redundante con Line Coverage
8. Test Count - no es indicador de calidad
9. Duplication Density - redundante con Duplicated Lines

**MANTENIBILIDAD (redundante):**
10. Maintainability Rating - redundante con MI

### CORE RECOMENDADO (20 métricas esenciales)

**Tamaño y Complejidad (4):**
1. Average Class Size (≤ 200 LOC)
2. Average Module Size (≤ 500 LOC)
3. WMC (≤ 20)
4. Total CC por clase (≤ 30)

**Cohesión y Acoplamiento (4):**
5. LCOM (≤ 1)
6. CBO (≤ 5)
7. Fan-In (contexto)
8. Fan-Out (≤ 7)

**Herencia (2):**
9. DIT (≤ 5)
10. NOP (≤ 1)

**Mantenibilidad (3):**
11. MI (> 20)
12. Technical Debt Ratio (< 5%)
13. Code Smells (0)

**Duplicación (2):**
14. Duplicated Lines (< 3%)
15. Duplicated Blocks (0)

**Testing (2):**
16. Line Coverage (> 80%)
17. Branch Coverage (> 75%)

**Documentación (2):**
18. README Presence (Sí)
19. Public API Documented (100%)

**Confiabilidad y Dependencias (2):**
20. Bugs (0)
21. Circular Imports (0)

---

## NOTAS IMPORTANTES

### Sobre COHESIÓN:
- **LCOM es suficiente**. Las variantes LCOM1-5 son refinamientos académicos sin valor práctico diferencial.
- TCC y LCC requieren análisis de grafos complejos sin herramientas disponibles.

### Sobre HERENCIA:
- **DIT es la métrica crítica**. Jerarquías profundas (>5) son problemáticas.
- **NOP detecta herencia múltiple** - problemática en Python.
- Las métricas SIX, AIF, MIF, PF son académicas sin adopción práctica.

### Sobre TESTING:
- **Line Coverage + Branch Coverage son suficientes**.
- Function/Class/Statement Coverage son redundantes.
- **MC/DC solo para IEC 62304** (dispositivos médicos críticos).
- **Mutation Score es avanzado** - solo para proyectos maduros.

### Sobre MANTENIBILIDAD:
- **MI es la métrica rey** - combina CC, LOC y Halstead Volume.
- Technical Debt Ratio es útil si usas SonarQube.
- Code Smells es un agregado útil de problemas de diseño.

### Sobre DUPLICACIÓN:
- **< 3% es el umbral industria**.
- Duplicated Lines y Duplication Density son la misma métrica.

### Contexto de Aplicación:
Estas métricas se miden **por clase o por módulo**, y algunas se agregan a nivel de proyecto.
