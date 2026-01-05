# MÉTRICAS DE CALIDAD - CONTEXTO: CÓDIGO
**Nivel: Función/Método y Escritura**

## CATEGORÍA: TAMAÑO Y VOLUMEN

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| LOC por función/método | Básico | Esencial | ≤ 20 líneas | radon, pylint | Métrica fundamental de simplicidad |
| SLOC por función | Básico | Complementaria | ≤ 15 líneas | radon | Sin comentarios ni blancos |
| LLOC por función | Intermedio | Complementaria | ≤ 10 sentencias | radon | Sentencias lógicas ejecutables |
| Comments por función | Básico | Complementaria | - | radon | Contexto: balance con código |
| Comment Ratio | Básico | Complementaria | 10-30% | radon | Ni demasiado ni poco |
| Blank Lines | Básico | Complementaria | - | radon | **INNECESARIA** - no aporta valor |

## CATEGORÍA: COMPLEJIDAD Y ESTRUCTURA

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| CC (Cyclomatic Complexity) | Básico | Esencial | ≤ 10 | radon, mccabe | Métrica fundamental |
| Cognitive Complexity | Intermedio | Esencial | ≤ 15 | SonarQube | Mejor que CC para comprensión humana |
| Nesting Depth | Básico | Esencial | ≤ 4 niveles | pylint | Indicador crítico de código difícil |
| Boolean Expression Complexity | Intermedio | Complementaria | ≤ 3 | pylint | Útil para condiciones complejas |
| Essential Complexity | Avanzado | Complementaria | - | custom | **SIN FUNDAMENTO PRÁCTICO** - académica |

## CATEGORÍA: HALSTEAD (NIVEL FUNCIÓN)

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Halstead Volume (V) | Avanzado | Complementaria | - | radon | Solo necesaria para calcular MI |
| Halstead Difficulty (D) | Avanzado | Complementaria | - | radon | **POCO VALOR PRÁCTICO** - académica |
| Halstead Effort (E) | Avanzado | Complementaria | - | radon | **POCO VALOR PRÁCTICO** - derivada |
| Halstead Time (T) | Avanzado | Complementaria | - | radon | **INNECESARIA** - sin evidencia empírica |
| Halstead Bugs (B) | Avanzado | Complementaria | - | radon | **INNECESARIA** - predicción no validada |
| Operadores Únicos (n₁) | Avanzado | Complementaria | - | radon | **INNECESARIA** - componente interno |
| Operandos Únicos (n₂) | Avanzado | Complementaria | - | radon | **INNECESARIA** - componente interno |
| Total Operadores (N₁) | Avanzado | Complementaria | - | radon | **INNECESARIA** - componente interno |
| Total Operandos (N₂) | Avanzado | Complementaria | - | radon | **INNECESARIA** - componente interno |
| Vocabulario (n) | Avanzado | Complementaria | - | radon | **INNECESARIA** - componente interno |
| Longitud (N) | Avanzado | Complementaria | - | radon | **INNECESARIA** - componente interno |
| Longitud Calculada (N̂) | Avanzado | Complementaria | - | radon | **INNECESARIA** - componente interno |

## CATEGORÍA: ESTILO Y CONVENCIONES (PYTHON)

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| PEP8 Violations | Básico | Esencial | 0 | flake8, pycodestyle | Calidad básica del código |
| Naming Conventions | Básico | Esencial | 0 violaciones | pylint | Legibilidad fundamental |
| Import Order | Básico | Complementaria | 0 violaciones | isort | Organización, no crítica |
| Type Hints Coverage | Intermedio | Complementaria | > 80% | mypy | Para proyectos medianos/grandes |
| Type Errors | Intermedio | Esencial | 0 | mypy | Crítico si usas type hints |
| Lint Score (Pylint) | Básico | Esencial | ≥ 8.0/10 | pylint | Agregado de calidad general |
| Lint Warnings | Básico | Esencial | 0 | pylint, flake8 | Problemas potenciales |
| Lint Errors | Básico | Esencial | 0 | pylint, flake8 | Problemas críticos |

## CATEGORÍA: DOCUMENTACIÓN

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Docstring Coverage | Básico | Esencial | 100% API pública | interrogate | Documentación fundamental |
| PEP257 Violations | Intermedio | Complementaria | 0 | pydocstyle | Si usas docstrings formales |
| Docstring Quality | Intermedio | Complementaria | - | pydocstyle | **SIN UMBRAL CLARO** - subjetiva |
| Missing Docstrings | Básico | Esencial | 0 en público | pylint, pydocstyle | Redundante con Coverage |

## CATEGORÍA: CONFIABILIDAD (NIVEL FUNCIÓN)

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Bare Excepts | Básico | Esencial | 0 | pylint, bandit | Mal manejo crítico de errores |
| Exception Types | Intermedio | Complementaria | - | ast | Análisis de tipos de excepciones |
| Error Handling Coverage | Intermedio | Complementaria | > 80% | custom | **DIFÍCIL DE MEDIR** - sin herramienta clara |
| Dead Code | Básico | Esencial | 0 | vulture, pylint | Limpieza de código |
| Unused Variables | Básico | Esencial | 0 | pylint | Código muerto |
| Unused Functions | Básico | Esencial | 0 | vulture | Funciones no llamadas |
| Assertion Count | Intermedio | Complementaria | - | ast | **SIN UMBRAL CLARO** - contexto específico |

## CATEGORÍA: SEGURIDAD (NIVEL FUNCIÓN)

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Insecure Functions | Básico | Esencial | 0 | bandit | eval(), exec(), pickle.loads() |
| Hardcoded Secrets | Básico | Esencial | 0 | detect-secrets, bandit | Seguridad crítica |
| SQL Injection Risk | Intermedio | Esencial | 0 | bandit | Para código con DB |
| XSS Risk | Intermedio | Esencial | 0 | bandit | Para código web |

## CATEGORÍA: LIMPIEZA Y MANTENIMIENTO

| Métrica | Nivel | Utilidad | Umbral | Herramienta | Observaciones |
|---------|-------|----------|--------|-------------|---------------|
| Unused Imports | Básico | Esencial | 0 | autoflake, pylint | Limpieza básica |
| Missing Imports | Básico | Esencial | 0 | pylint | Errores de ejecución |

---

## RESUMEN CUANTITATIVO

### Por Utilidad
- **Esenciales:** 21 métricas
- **Complementarias útiles:** 12 métricas
- **Innecesarias/sin fundamento:** 13 métricas

### Métricas INNECESARIAS o SIN FUNDAMENTO
1. **Blank Lines** - no aporta valor de calidad
2. **Essential Complexity** - académica, sin aplicación práctica
3. **Todo Halstead excepto Volume** - 11 métricas académicas sin valor predictivo validado
4. **Docstring Quality** - subjetiva, sin umbral claro
5. **Assertion Count** - contexto demasiado específico
6. **Error Handling Coverage** - sin herramienta clara

### CORE RECOMENDADO (15 métricas esenciales)
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
15. Type Errors (0 si usas type hints)

---

**NOTAS IMPORTANTES:**

1. **Halstead:** Mantener solo Volume y solo si calculas Maintainability Index. Todo lo demás es ruido académico.

2. **Type Hints:** Si el proyecto usa type hints, entonces Type Errors pasa a esencial y Type Hints Coverage a complementaria útil.

3. **Seguridad:** SQL Injection y XSS solo son relevantes si el código interactúa con DB o web.

4. **Contexto de aplicación:** Estas métricas se miden **por función/método individual**, no a nivel agregado.
