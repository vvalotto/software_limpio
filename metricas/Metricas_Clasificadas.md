# CATÁLOGO DE MÉTRICAS CLASIFICADO
## Ingeniería de Software en Sistemas Embebidos

**Clasificación por:**
- **Nivel**: Básico / Intermedio / Avanzado
- **Contexto**: Código / Diseño / Arquitectura
- **Utilidad**: Esencial / Complementaria

---

## 1. MÉTRICAS DE TAMAÑO

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| LOC (Lines of Code) | Básico | Código | Esencial | < 500 por módulo | radon, cloc | Métrica base fundamental |
| SLOC (Source LOC) | Básico | Código | Esencial | - | radon, cloc | Más precisa que LOC |
| LLOC (Logical LOC) | Intermedio | Código | Complementaria | - | radon | Útil para estimar esfuerzo |
| Comments | Básico | Código | Complementaria | - | radon, pylint | - |
| Blank Lines | Básico | Código | Complementaria | - | radon, cloc | **INNECESARIA** - poco valor |
| Comment Ratio | Básico | Código | Complementaria | 10-30% | radon | - |
| Files Count | Básico | Diseño | Complementaria | - | cloc | - |
| Classes Count | Básico | Diseño | Complementaria | - | radon, pylint | - |
| Functions Count | Básico | Código | Complementaria | - | radon, pylint | - |
| Modules Count | Básico | Diseño | Complementaria | - | pydeps | - |
| Packages Count | Básico | Arquitectura | Complementaria | - | pydeps | - |
| Average Module Size | Intermedio | Diseño | Esencial | < 500 LOC | radon | - |
| Average Class Size | Intermedio | Diseño | Esencial | < 300 LOC | radon | - |
| Average Method Size | Básico | Código | Esencial | < 50 LOC | radon | - |

---

## 2. MÉTRICAS DE COMPLEJIDAD

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| CC (Cyclomatic Complexity) | Básico | Código | Esencial | ≤ 10 | radon, pylint | **FUNDAMENTAL** |
| Cognitive Complexity | Intermedio | Código | Esencial | ≤ 15 | SonarQube, flake8 | Más intuitiva que CC |
| Total CC | Intermedio | Diseño | Complementaria | - | radon | Suma de proyecto |
| Average CC | Intermedio | Diseño | Esencial | ≤ 5 | radon | Indicador de salud |
| Max CC | Básico | Código | Esencial | ≤ 10 | radon | Detecta hotspots |
| CC Distribution | Intermedio | Diseño | Complementaria | Mayoría A-B | radon | Visualización útil |
| Nesting Depth | Básico | Código | Esencial | ≤ 4 | pylint | Indicador de claridad |
| Boolean Expression Complexity | Intermedio | Código | Complementaria | - | pylint | - |
| Essential Complexity | Avanzado | Código | Complementaria | - | custom | **SIN HERRAMIENTA** - descartar |

---

## 3. MÉTRICAS DE HALSTEAD

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| Operadores Únicos (n₁) | Avanzado | Código | Complementaria | - | radon | **ACADÉMICA** - poco valor práctico |
| Operandos Únicos (n₂) | Avanzado | Código | Complementaria | - | radon | **ACADÉMICA** - poco valor práctico |
| Total Operadores (N₁) | Avanzado | Código | Complementaria | - | radon | **ACADÉMICA** - poco valor práctico |
| Total Operandos (N₂) | Avanzado | Código | Complementaria | - | radon | **ACADÉMICA** - poco valor práctico |
| Vocabulario (n) | Avanzado | Código | Complementaria | - | radon | **ACADÉMICA** - poco valor práctico |
| Longitud (N) | Avanzado | Código | Complementaria | - | radon | **ACADÉMICA** - poco valor práctico |
| Longitud Calculada (N̂) | Avanzado | Código | Complementaria | - | radon | **ACADÉMICA** - poco valor práctico |
| Volumen (V) | Avanzado | Código | Complementaria | - | radon | Usada en MI, sino descartar |
| Dificultad (D) | Avanzado | Código | Complementaria | - | radon | **ACADÉMICA** - poco valor práctico |
| Esfuerzo (E) | Avanzado | Código | Complementaria | - | radon | **ACADÉMICA** - poco valor práctico |
| Tiempo de Programación (T) | Avanzado | Código | Complementaria | - | radon | **ACADÉMICA** - poco valor práctico |
| Bugs Estimados (B) | Avanzado | Código | Complementaria | - | radon | **POCO CONFIABLE** |

**RECOMENDACIÓN**: Halstead completo es **DESECHABLE** excepto Volumen (V) usado en cálculo de MI.

---

## 4. MÉTRICAS DE MANTENIBILIDAD

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| Maintainability Index (MI) | Intermedio | Diseño | Esencial | > 20 (mejor > 65) | radon, SonarQube | **MÉTRICA CLAVE** |
| MI sin comentarios | Intermedio | Diseño | Complementaria | - | radon | Variante más estricta |
| Technical Debt | Avanzado | Diseño | Esencial | - | SonarQube | En horas de trabajo |
| Technical Debt Ratio | Avanzado | Diseño | Esencial | < 5% | SonarQube | % del desarrollo |
| Code Smells | Intermedio | Diseño | Esencial | 0 | SonarQube, pylint | Indicador de problemas |
| Maintainability Rating | Intermedio | Diseño | Complementaria | A | SonarQube | Escala A-E |

---

## 5. MÉTRICAS DE COHESIÓN

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| LCOM (Lack of Cohesion) | Intermedio | Diseño | Esencial | Bajo | pylint | **USAR UNA SOLA VARIANTE** |
| LCOM1 | Avanzado | Diseño | Complementaria | - | custom | **REDUNDANTE** - elegir una |
| LCOM2 | Avanzado | Diseño | Complementaria | - | custom | **REDUNDANTE** - elegir una |
| LCOM3 | Avanzado | Diseño | Complementaria | - | custom | **REDUNDANTE** - elegir una |
| LCOM4 | Avanzado | Diseño | Complementaria | - | custom | **REDUNDANTE** - elegir una |
| LCOM5 | Avanzado | Diseño | Complementaria | - | custom | **REDUNDANTE** - elegir una |
| TCC (Tight Class Cohesion) | Avanzado | Diseño | Complementaria | > 0.5 | custom | **SIN HERRAMIENTA** |
| LCC (Loose Class Cohesion) | Avanzado | Diseño | Complementaria | > 0.8 | custom | **SIN HERRAMIENTA** |
| Cohesion Ratio | Intermedio | Diseño | Complementaria | > 0.7 | custom | **SIN HERRAMIENTA** |

**RECOMENDACIÓN**: Elegir SOLO LCOM estándar. El resto es **REDUNDANTE** o académico.

---

## 6. MÉTRICAS DE ACOPLAMIENTO

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| CBO (Coupling Between Objects) | Intermedio | Diseño | Esencial | ≤ 5 | pylint, SonarQube | **MÉTRICA CLAVE** |
| Fan-In | Intermedio | Diseño | Complementaria | - | pydeps | Reusabilidad |
| Fan-Out | Intermedio | Diseño | Esencial | Bajo | pydeps | Dependencias |
| Imports Count | Básico | Código | Complementaria | < 10 | pylint | - |
| External Dependencies | Intermedio | Arquitectura | Esencial | Mínimo | pipdeptree | - |
| Internal Dependencies | Intermedio | Diseño | Complementaria | - | pydeps | - |
| Dependency Cycles | Intermedio | Arquitectura | Esencial | 0 | pydeps, import-linter | **CRÍTICO** |
| Afferent Coupling (Ca) | Avanzado | Arquitectura | Complementaria | - | custom | Ver métricas Martin |
| Efferent Coupling (Ce) | Avanzado | Arquitectura | Complementaria | - | custom | Ver métricas Martin |
| Coupling Factor (CF) | Avanzado | Arquitectura | Complementaria | Bajo | custom | **SIN HERRAMIENTA** |

---

## 7. MÉTRICAS DE ROBERT C. MARTIN (PAQUETES)

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| Ca (Afferent Coupling) | Avanzado | Arquitectura | Esencial | Contexto | custom | Para arquitectura |
| Ce (Efferent Coupling) | Avanzado | Arquitectura | Esencial | Contexto | custom | Para arquitectura |
| I (Instability) | Avanzado | Arquitectura | Esencial | 0-1 (contexto) | custom | Ce/(Ca+Ce) |
| A (Abstractness) | Avanzado | Arquitectura | Complementaria | 0-1 (contexto) | custom | Ratio abstractas |
| D (Distance) | Avanzado | Arquitectura | Esencial | ≈ 0 | custom | Distancia a secuencia |
| D' (Normalized Distance) | Avanzado | Arquitectura | Complementaria | ≈ 0 | custom | Normalizada |

**RECOMENDACIÓN**: Conjunto completo muy útil para **arquitectura avanzada**.

---

## 8. MÉTRICAS CK (CHIDAMBER-KEMERER)

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| WMC (Weighted Methods per Class) | Intermedio | Diseño | Esencial | ≤ 20 | radon, pylint | Suma de CC |
| DIT (Depth of Inheritance Tree) | Intermedio | Diseño | Esencial | ≤ 5 | pylint | Profundidad herencia |
| NOC (Number of Children) | Intermedio | Diseño | Complementaria | - | pylint | Hijos directos |
| CBO (Coupling Between Objects) | Intermedio | Diseño | Esencial | ≤ 5 | pylint | **YA EN ACOPLAMIENTO** |
| RFC (Response for Class) | Intermedio | Diseño | Complementaria | ≤ 50 | custom | Métodos ejecutables |
| LCOM (Lack of Cohesion) | Intermedio | Diseño | Esencial | Bajo | custom | **YA EN COHESIÓN** |

**NOTA**: CBO y LCOM duplican métricas anteriores.

---

## 9. MÉTRICAS DE HERENCIA

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| DIT | Intermedio | Diseño | Esencial | ≤ 5 | pylint, ast | **DUPLICADA de CK** |
| NOC | Intermedio | Diseño | Complementaria | - | ast | **DUPLICADA de CK** |
| NOP (Number of Parents) | Intermedio | Diseño | Complementaria | ≤ 2 | ast | Herencia múltiple |
| SIX (Specialization Index) | Avanzado | Diseño | Complementaria | - | custom | **POCO USADA** |
| AIF (Attribute Inheritance Factor) | Avanzado | Diseño | Complementaria | - | custom | **ACADÉMICA** |
| MIF (Method Inheritance Factor) | Avanzado | Diseño | Complementaria | - | custom | **ACADÉMICA** |
| PF (Polymorphism Factor) | Avanzado | Diseño | Complementaria | - | custom | **ACADÉMICA** |
| Abstract Classes Count | Intermedio | Diseño | Complementaria | - | ast | - |
| Interfaces Count | Intermedio | Diseño | Complementaria | - | ast | Protocolos/ABC |

**RECOMENDACIÓN**: DIT, NOC, NOP suficientes. SIX, AIF, MIF, PF son **ACADÉMICAS**.

---

## 10. MÉTRICAS DE DUPLICACIÓN

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| Duplicated Lines | Básico | Código | Esencial | < 5% | SonarQube, pylint | - |
| Duplicated Blocks | Básico | Código | Esencial | 0 | SonarQube, jscpd | - |
| Duplicated Files | Básico | Código | Complementaria | 0 | SonarQube | - |
| Duplication Density | Básico | Código | Esencial | < 5% | SonarQube | **MÉTRICA RESUMEN** |
| Clone Classes | Intermedio | Código | Complementaria | - | jscpd | Grupos de clones |
| Clone Coverage | Intermedio | Código | Complementaria | - | jscpd | % código clonado |

---

## 11. MÉTRICAS DE DOCUMENTACIÓN

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| Docstring Coverage | Básico | Código | Esencial | > 80% | interrogate | **MUY IMPORTANTE** |
| Comment Density | Básico | Código | Complementaria | 10-30% | radon | **DUPLICADA** |
| Missing Docstrings | Básico | Código | Esencial | 0 | pylint, pydocstyle | - |
| Docstring Quality | Intermedio | Código | Complementaria | 100% | pydocstyle | Estándar Google/NumPy |
| README Presence | Básico | Diseño | Complementaria | Sí | custom | - |
| Documentation Ratio | Intermedio | Código | Complementaria | - | custom | **SIMILAR A COMMENT DENSITY** |
| Public API Documented | Intermedio | Diseño | Esencial | 100% | interrogate | API pública |

---

## 12. MÉTRICAS DE TESTING Y COBERTURA

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| Line Coverage | Básico | Código | Esencial | > 80% | coverage.py | **FUNDAMENTAL** |
| Branch Coverage | Intermedio | Código | Esencial | > 70% | coverage.py | Más estricta |
| Function Coverage | Básico | Código | Complementaria | 100% | coverage.py | - |
| Class Coverage | Básico | Diseño | Complementaria | 100% | coverage.py | - |
| Statement Coverage | Básico | Código | Complementaria | - | coverage.py | **SIMILAR A LINE** |
| Condition Coverage | Intermedio | Código | Complementaria | - | coverage.py | - |
| MC/DC Coverage | Avanzado | Código | Complementaria | - | custom | Para sistemas críticos |
| Test Count | Básico | Código | Complementaria | - | pytest | - |
| Test/Code Ratio | Intermedio | Código | Complementaria | > 1:1 | custom | - |
| Mutation Score | Avanzado | Código | Complementaria | > 60% | mutmut | Calidad de tests |
| Tests Passed/Failed | Básico | Código | Esencial | 100% pass | pytest | - |
| Test Execution Time | Básico | Código | Complementaria | - | pytest | - |

---

## 13. MÉTRICAS DE SEGURIDAD

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| Vulnerabilities | Intermedio | Código | Esencial | 0 | bandit, safety | - |
| Security Hotspots | Intermedio | Código | Complementaria | 0 | SonarQube, bandit | - |
| Dependency Vulnerabilities | Intermedio | Arquitectura | Esencial | 0 | safety, pip-audit | **CRÍTICO** |
| Hardcoded Secrets | Básico | Código | Esencial | 0 | detect-secrets | - |
| SQL Injection Risk | Intermedio | Código | Complementaria | 0 | bandit | Si aplica |
| XSS Risk | Intermedio | Código | Complementaria | 0 | bandit | Si aplica |
| Insecure Functions | Básico | Código | Esencial | 0 | bandit | eval(), exec() |
| Security Rating | Intermedio | Diseño | Complementaria | A | SonarQube | Escala A-E |

---

## 14. MÉTRICAS DE ESTILO Y CONVENCIONES (PYTHON)

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| PEP8 Violations | Básico | Código | Esencial | 0 | flake8, pycodestyle | **FUNDAMENTAL** |
| PEP257 Violations | Básico | Código | Complementaria | 0 | pydocstyle | Docstrings |
| Naming Conventions | Básico | Código | Esencial | 0 | pylint | - |
| Import Order | Básico | Código | Complementaria | 0 | isort | - |
| Type Hints Coverage | Intermedio | Código | Esencial | > 80% | mypy | Cada vez más importante |
| Type Errors | Intermedio | Código | Esencial | 0 | mypy, pyright | - |
| Lint Warnings | Básico | Código | Complementaria | 0 | pylint, flake8 | - |
| Lint Errors | Básico | Código | Esencial | 0 | pylint, flake8 | - |
| Pylint Score | Básico | Código | Esencial | > 8.0 | pylint | **MÉTRICA RESUMEN** |

---

## 15. MÉTRICAS DE DEPENDENCIAS

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| Direct Dependencies | Básico | Arquitectura | Esencial | Mínimo | pip, pipdeptree | - |
| Transitive Dependencies | Intermedio | Arquitectura | Complementaria | - | pipdeptree | - |
| Total Dependencies | Intermedio | Arquitectura | Complementaria | Bajo | pipdeptree | - |
| Outdated Dependencies | Básico | Arquitectura | Esencial | 0 | pip-review | Seguridad |
| Dependency Depth | Intermedio | Arquitectura | Complementaria | Bajo | pipdeptree | - |
| Circular Imports | Intermedio | Diseño | Esencial | 0 | pylint, import-linter | **CRÍTICO** |
| Import Violations | Intermedio | Arquitectura | Esencial | 0 | import-linter | Clean Arch |
| Unused Imports | Básico | Código | Complementaria | 0 | autoflake, pylint | - |
| Missing Imports | Básico | Código | Esencial | 0 | pylint | - |

---

## 16. MÉTRICAS DE DSM (DESIGN STRUCTURE MATRIX)

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| Dependency Matrix | Avanzado | Arquitectura | Complementaria | - | pydeps + script | **AVANZADO** |
| Propagation Cost | Avanzado | Arquitectura | Complementaria | Bajo | custom | **SIN HERRAMIENTA** |
| Cluster Count | Avanzado | Arquitectura | Complementaria | - | custom | **SIN HERRAMIENTA** |
| Cyclic Dependencies | Avanzado | Arquitectura | Esencial | 0 | pydeps | **DUPLICADA** |
| Layering Violations | Avanzado | Arquitectura | Esencial | 0 | import-linter | **DUPLICADA** |
| Matrix Density | Avanzado | Arquitectura | Complementaria | - | custom | **SIN HERRAMIENTA** |
| Bandwidth | Avanzado | Arquitectura | Complementaria | - | custom | **SIN HERRAMIENTA** |

**RECOMENDACIÓN**: DSM es **DEMASIADO AVANZADO** para formación. Cyclic Dependencies y Layering ya cubiertas.

---

## 17. MÉTRICAS DE ARQUITECTURA LIMPIA

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| Layer Violations | Avanzado | Arquitectura | Esencial | 0 | import-linter | **DUPLICADA** |
| Domain Purity | Avanzado | Arquitectura | Esencial | 100% | custom | Sin deps externas |
| Adapter Count | Avanzado | Arquitectura | Complementaria | - | manual/ast | - |
| Use Case Count | Avanzado | Arquitectura | Complementaria | - | manual/ast | - |
| Entity Count | Avanzado | Arquitectura | Complementaria | - | manual/ast | - |
| Inward Dependencies | Avanzado | Arquitectura | Esencial | Mayoría | pydeps | Hacia el centro |
| Outward Dependencies | Avanzado | Arquitectura | Esencial | 0 | pydeps | Violaciones |

---

## 18. MÉTRICAS DE CONFIABILIDAD

| Métrica | Nivel | Contexto | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|----------|---------|-------------|---------------|
| Bugs | Intermedio | Código | Esencial | 0 | SonarQube, pylint | Defectos potenciales |
| Reliability Rating | Intermedio | Diseño | Complementaria | A | SonarQube | Escala A-E |
| Error Handling Coverage | Intermedio | Código | Complementaria | - | custom | Try/except |
| Exception Types | Intermedio | Código | Complementaria | - | ast | Tipos usados |
| Bare Excepts | Básico | Código | Esencial | 0 | pylint, bandit | **MAL PRÁCTICA** |
| Assertion Count | Básico | Código | Complementaria | - | ast | - |
| Dead Code | Básico | Código | Complementaria | 0 | vulture, pylint | Código inalcanzable |
| Unused Variables | Básico | Código | Complementaria | 0 | pylint, vulture | - |
| Unused Functions | Básico | Código | Complementaria | 0 | vulture | - |

---

## RESUMEN EJECUTIVO

### MÉTRICAS ESENCIALES POR NIVEL

#### BÁSICO (15 métricas core)
1. LOC, SLOC
2. **Cyclomatic Complexity (CC)**
3. Average Method Size
4. Nesting Depth
5. **Maintainability Index (MI)**
6. **Duplicated Lines/Density**
7. **Docstring Coverage**
8. **Line Coverage**
9. Tests Passed/Failed
10. **PEP8 Violations**
11. **Pylint Score**
12. Hardcoded Secrets
13. Insecure Functions
14. Missing Imports
15. Bare Excepts

#### INTERMEDIO (12 métricas adicionales)
16. Cognitive Complexity
17. Average CC
18. Code Smells
19. Technical Debt Ratio
20. **CBO (Coupling)**
21. **Fan-Out**
22. WMC, DIT
23. Branch Coverage
24. Type Hints Coverage
25. Dependency Cycles
26. Circular Imports
27. Dependency Vulnerabilities

#### AVANZADO (8 métricas adicionales)
28. Métricas de Robert Martin (Ca, Ce, I, D)
29. Domain Purity
30. Inward/Outward Dependencies
31. Mutation Score
32. MC/DC Coverage (sistemas críticos)

### MÉTRICAS DESECHABLES

**DEFINITIVAMENTE INNECESARIAS:**
- Blank Lines
- Halstead completo (excepto V en MI)
- LCOM2-5 (redundantes)
- TCC, LCC, Cohesion Ratio (sin herramienta)
- SIX, AIF, MIF, PF (académicas)
- DSM completo (excepto lo ya cubierto)
- Essential Complexity (sin herramienta)
- Coupling Factor (sin herramienta)
- Propagation Cost, Cluster Count, Matrix Density, Bandwidth (sin herramienta)

**TOTAL**: ~40 de 155 métricas son **desechables** por ser redundantes, académicas o sin herramientas.

### CORE RECOMENDADO: 35 MÉTRICAS

Para un programa de formación efectivo, concentrarse en las **35 métricas esenciales** marcadas arriba.
