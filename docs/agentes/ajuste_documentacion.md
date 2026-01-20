# Ajuste de Documentación - Agentes de Calidad

**Fecha de inicio:** 2026-01-20
**Objetivo:** Alinear especificación, guía de implementación y plan del proyecto

---

## Contexto

Se detectaron inconsistencias entre los tres documentos principales:
- `docs/agentes/especificacion_agentes_calidad.md`
- `docs/agentes/guia_implementacion_agentes.md`
- `plan/plan_proyecto.md`

**Problemas identificados:**
1. Estructura de configuración (3 rutas diferentes propuestas)
2. Modelo de distribución no definido claramente
3. Terminología "agente" vs "checker/linter"
4. Proceso de integración en otros proyectos ambiguo

---

## Plan de Trabajo

### Fase 1: Decisiones Arquitectónicas Fundamentales ✅

**Objetivo:** Resolver decisiones clave que afectan todo el diseño
**Estado:** COMPLETADA - 2026-01-20

**Tareas:**
- [x] Decisión #1: Modelo de distribución ✅ Opción D - Híbrido
- [x] Decisión #2: Modelo de integración ✅ Opción D - Todos los modelos
- [x] Decisión #3: Estructura de configuración ✅ Opción C - pyproject.toml
- [x] Decisión #4: Nomenclatura y terminología ✅ Opción A - Todos son agentes
- [x] Decisión #5: Alcance de IA en CodeGuard ✅ Opción B - IA opcional

### Fase 2: Actualización de Especificación

**Archivos a actualizar:**
- [ ] `docs/agentes/especificacion_agentes_calidad.md`

**Secciones a agregar/modificar:**
- [ ] Sección "Modelo de Distribución"
- [ ] Sección "Integración en Proyectos"
- [ ] Ajustar configuraciones según decisiones

### Fase 3: Actualización de Guía de Implementación

**Archivos a actualizar:**
- [ ] `docs/agentes/guia_implementacion_agentes.md`

**Cambios:**
- [ ] Alinear con modelo de distribución elegido
- [ ] Actualizar ejemplos de instalación
- [ ] Actualizar rutas de configuración

### Fase 4: Actualización del Plan

**Archivos a actualizar:**
- [ ] `plan/plan_proyecto.md`

**Cambios:**
- [ ] Roadmap actualizado con decisiones
- [ ] Criterios de éxito precisos
- [ ] Prioridades ajustadas

### Fase 5: Documentación de Integración

**Archivos a crear:**
- [ ] `docs/guias/integracion.md` - Guía de integración en otros proyectos

---

## Decisiones Arquitectónicas

### Decisión #1: Modelo de Distribución

**Fecha:** 2026-01-20
**Estado:** ✅ Decidido

**Opciones evaluadas:**

#### A) Paquete Instalable (como black, pylint)
```bash
pip install quality-agents
codeguard .
```

**Pros:**
- ✅ Profesional y estándar
- ✅ Versionado centralizado
- ✅ Fácil actualización
- ✅ Publicable en PyPI
- ✅ Reutilizable entre proyectos

**Contras:**
- ❌ Requiere publicación/mantenimiento
- ❌ Los usuarios dependen de versión externa

---

#### B) Framework Integrable (como pre-commit hooks)
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.1.0
    hooks:
      - id: codeguard
```

**Pros:**
- ✅ Integración declarativa
- ✅ Versionado por proyecto
- ✅ Estándar para herramientas de calidad

**Contras:**
- ❌ Limitado al ecosistema pre-commit
- ❌ Menos flexible para uso standalone

---

#### C) Script Standalone (copiar al proyecto)
```bash
cp software_limpio/quality_agents/*.py mi_proyecto/quality_agents/
```

**Pros:**
- ✅ Máxima flexibilidad
- ✅ Sin dependencias externas
- ✅ Fácil para estudiantes (ver el código)

**Contras:**
- ❌ Sincronización manual de actualizaciones
- ❌ Duplicación de código
- ❌ No escalable

---

#### D) Híbrido (Paquete + Hooks)
```bash
# Opción 1: Instalar como paquete
pip install quality-agents
codeguard .

# Opción 2: Usar via pre-commit
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.1.0
    hooks:
      - id: codeguard
```

**Pros:**
- ✅ Máxima flexibilidad
- ✅ Soporta ambos casos de uso
- ✅ Usuarios eligen su modelo preferido

**Contras:**
- ❌ Más complejo de mantener
- ❌ Requiere documentar ambos modelos

---

**Criterios de evaluación:**

| Criterio | Peso | A | B | C | D |
|----------|------|---|---|---|---|
| Contexto educativo (estudiantes) | 30% | ? | ? | ? | ? |
| Uso profesional | 25% | ? | ? | ? | ? |
| Facilidad de mantenimiento | 20% | ? | ? | ? | ? |
| Escalabilidad | 15% | ? | ? | ? | ? |
| Flexibilidad | 10% | ? | ? | ? | ? |

**Decisión tomada:** ✅ **Opción D - Híbrido (Paquete + Hooks)**

**Justificación:** Adopción profesional. El modelo híbrido permite que el framework sea usado como herramienta estándar de la industria (via pip/pre-commit) mientras mantiene flexibilidad para diferentes contextos de uso.

**Implicaciones:**
- Desarrollar paquete instalable vía `pip install quality-agents`
- Soportar también integración vía pre-commit framework
- Documentar ambos modelos de uso
- Crear `.pre-commit-hooks.yaml` en el repo

---

### Decisión #2: Modelo de Integración

**Fecha:** 2026-01-20
**Estado:** ✅ Decidido

**Pregunta:** ¿Cómo se integran los agentes en un proyecto existente?

**Opciones:**

#### A) Hook Git Manual
```bash
# En el proyecto destino
pip install quality-agents
echo '#!/bin/bash\ncodeguard' > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

#### B) Framework pre-commit
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.1.0
    hooks:
      - id: codeguard
        args: [--config=.codeguard.yml]
```

#### C) GitHub Actions
```yaml
# .github/workflows/quality.yml
- name: Run CodeGuard
  run: |
    pip install quality-agents
    codeguard .
```

#### D) Todos los anteriores (recomendado)

**Decisión tomada:** ✅ **Opción D - Todos los Modelos de Integración**

**Justificación:** Máxima flexibilidad para adopción profesional. Soportar múltiples formas de integración permite que empresas, equipos y estudiantes elijan el modelo que mejor se adapte a su workflow existente.

**Implicaciones:**
- Crear archivo `.pre-commit-hooks.yaml` en el repositorio
- Documentar en README las 4 formas de uso:
  1. Uso directo desde terminal (`codeguard .`)
  2. Pre-commit framework (`.pre-commit-config.yaml`)
  3. Hook Git manual (script en `.git/hooks/`)
  4. GitHub Actions (workflow example)
- Crear `docs/guias/integracion.md` con ejemplos detallados
- Probar todas las integraciones en CI/CD

---

### Decisión #3: Estructura de Configuración

**Fecha:** 2026-01-20
**Estado:** ✅ Decidido

**Pregunta:** ¿Dónde se ubican los archivos de configuración?

**Opciones detectadas en la documentación actual:**

| Documento | Ruta Propuesta |
|-----------|----------------|
| Especificación | `.codeguard.yml` (raíz del proyecto) |
| Guía Implementación | `.quality_control/codeguard/config.yml` |
| Implementación actual | `configs/codeguard.yml` (dentro del paquete) |

**Propuesta de unificación:**

#### Opción A: Raíz del proyecto usuario (estándar de herramientas)
```
mi_proyecto/
├── .codeguard.yml
├── .designreviewer.yml
└── .architectanalyst.yml
```
**Ejemplo:** Similar a `.flake8`, `.pylintrc`, `.mypy.ini`

#### Opción B: Directorio .quality/
```
mi_proyecto/
└── .quality/
    ├── codeguard.yml
    ├── designreviewer.yml
    └── architectanalyst.yml
```
**Ejemplo:** Similar a `.github/`, `.vscode/`

#### Opción C: pyproject.toml (moderno)
```toml
[tool.codeguard]
min_pylint_score = 8.0
max_cyclomatic_complexity = 10

[tool.designreviewer]
blocking_thresholds.class_size = 200
```
**Ejemplo:** Similar a black, ruff, pytest

#### Opción D: Híbrido (buscar en orden)
1. `pyproject.toml` (prioridad)
2. `.codeguard.yml` (si existe)
3. `.quality/codeguard.yml` (si existe)
4. Defaults internos

**Decisión tomada:** ✅ **Opción C - pyproject.toml con fallback a .yml**

**Justificación:** Estándar moderno de Python (PEP 518). Todas las herramientas profesionales (black, ruff, pytest, mypy) usan pyproject.toml. Centraliza configuración en un solo archivo. Para compatibilidad, se buscará primero en pyproject.toml y luego en `.codeguard.yml` como fallback.

**Implicaciones:**
- Implementar parser de configuración desde pyproject.toml
- Sección `[tool.codeguard]`, `[tool.designreviewer]`, `[tool.architectanalyst]`
- Fallback a `.codeguard.yml`, `.designreviewer.yml`, `.architectanalyst.yml`
- Documentar ambas formas en README (pyproject.toml recomendado)
- Actualizar ejemplos en toda la documentación
- Modificar `configs/` del paquete como templates/ejemplos, no configs activas

**Ejemplo de configuración:**
```toml
# pyproject.toml
[tool.codeguard]
min_pylint_score = 8.0
max_cyclomatic_complexity = 10
check_pep8 = true
check_security = true

[tool.designreviewer]
blocking_thresholds = { class_size = 200, cbo = 5, wmc = 20 }
ai_suggestions = { enabled = true, model = "claude-sonnet-4" }

[tool.architectanalyst]
thresholds = { distance_main_sequence = 0.2, tech_debt_ratio = 5.0 }
```

---

### Decisión #4: Nomenclatura y Terminología

**Fecha:** 2026-01-20
**Estado:** ✅ Decidido

**Pregunta:** ¿Es apropiado llamar "agentes" a los tres componentes?

**Análisis:**

| Componente | Usa IA | Razona | Aprende | ¿Es agente? |
|------------|--------|--------|---------|-------------|
| CodeGuard | ❌ | ❌ | ❌ | Cuestionable |
| DesignReviewer | ✅ | ✅ | ❌ | Sí |
| ArchitectAnalyst | ✅ | ✅ | ❌ | Sí |

**Opciones:**

#### A) Mantener "agente" para los 3
- Agregar IA simple a CodeGuard para justificar el nombre
- Ejemplo: Sugerencias contextuales con Claude

#### B) Renombrar CodeGuard
- `CodeGuard` → `QualityChecker` o `PreCommitChecker`
- Solo DesignReviewer y ArchitectAnalyst son "agentes"

#### C) Usar término genérico
- "Herramientas de control de calidad"
- CodeGuard = checker, otros = agentes

#### D) Mantener como está
- Es marketing/naming, no técnico
- "Agente" suena mejor que "script"

**Decisión tomada:** ✅ **Opción A - Mantener "agente" agregando IA a CodeGuard**

**Justificación:** Coherencia conceptual y técnica. Los tres componentes serán verdaderos "agentes" al usar IA para razonar y sugerir mejoras. CodeGuard tendrá IA ligera (opcional), DesignReviewer IA media (siempre), ArchitectAnalyst IA profunda (siempre). Esto justifica la nomenclatura y agrega valor diferencial.

**Implicaciones:**
- Agregar integración opcional con Claude API en CodeGuard
- Configuración `[tool.codeguard.ai]` en pyproject.toml
- IA solo se activa si:
  - Usuario la habilita en config (`ai_explanations = true`)
  - Hay errores detectados (no en commits limpios)
- Mantiene restricción < 5s en casos comunes (sin errores)
- Agregar variable de entorno `ANTHROPIC_API_KEY`
- Actualizar tabla comparativa:

| Agente | Momento | IA | Uso de IA |
|--------|---------|-----|-----------|
| CodeGuard | Pre-commit | Opcional | Explicaciones de errores |
| DesignReviewer | PR/Review | Siempre | Sugerencias de refactoring |
| ArchitectAnalyst | Sprint-end | Siempre | Análisis predictivo |

---

### Decisión #5: Alcance de IA en CodeGuard

**Fecha:** 2026-01-20
**Estado:** ✅ Decidido (derivada de Decisión #4)

**Pregunta:** ¿Debe CodeGuard usar IA o ser solo un agregador de linters?

**Contexto:**
- Restricción de tiempo: < 5 segundos
- Llamada a API Claude: ~1-3 segundos
- Espacio para IA: Limitado pero posible

**Opciones:**

#### A) Sin IA (solo linters)
```python
def run(self):
    results = []
    results.extend(flake8_check())
    results.extend(pylint_check())
    results.extend(bandit_check())
    return results  # Solo resultados de herramientas
```
**Pro:** Simple, rápido, predecible
**Contra:** No es un "agente" real

#### B) IA opcional para explicaciones
```python
def run(self):
    results = run_all_checks()

    if config.ai_explanations and has_errors(results):
        # Solo si hay errores Y user lo habilita
        ai_explanation = claude_explain_errors(results)  # +2s
        results.append(ai_explanation)

    return results
```
**Pro:** Balance entre velocidad y valor agregado
**Contra:** Comportamiento inconsistente (a veces usa IA, a veces no)

#### C) IA siempre activa
```python
def run(self):
    results = run_all_checks()
    ai_summary = claude_summarize(results)  # +2s
    return results + [ai_summary]
```
**Pro:** Consistente, siempre es "agente"
**Contra:** Puede exceder los 5 segundos, costo de API

#### D) Sin IA en CodeGuard, solo en los otros
**Recomendación:** Mantener la separación de responsabilidades
- CodeGuard = Rápido, sin IA (< 5s)
- DesignReviewer = Con IA (2-5 min)
- ArchitectAnalyst = Con IA (10-30 min)

**Decisión tomada:** ✅ **Opción B - IA Opcional para Explicaciones**

**Justificación:** Esta decisión es consecuencia directa de la Decisión #4. Para que CodeGuard sea un "agente" legítimo, debe usar IA, pero de forma inteligente que no comprometa el requisito de < 5 segundos. La IA solo se activa cuando hay valor real: errores detectados + usuario lo habilita.

**Implicaciones técnicas:**
- Implementar lógica condicional de IA en `src/quality_agents/codeguard/agent.py`
- Agregar módulo `src/quality_agents/codeguard/ai_suggestions.py`
- Configuración en pyproject.toml:
  ```toml
  [tool.codeguard.ai]
  enabled = false  # Deshabilitado por default (opt-in)
  explain_errors = true  # Explicar errores si habilitado
  suggest_fixes = true   # Sugerir correcciones
  max_tokens = 500       # Respuesta breve
  ```
- Flujo de ejecución:
  1. Ejecutar todos los linters (flake8, pylint, bandit, radon)
  2. Si hay errores AND config.ai.enabled = true:
     - Enviar errores a Claude
     - Pedir explicación breve + sugerencia de fix
     - Agregar al output
  3. Si no hay errores: terminar sin llamar IA (< 2s)
- Documentar que IA es opcional y requiere API key
- Agregar ejemplo de configuración con/sin IA

**Tiempos esperados:**
- Commits limpios (sin errores): ~2 segundos (sin IA)
- Commits con errores + IA habilitada: ~4 segundos
- Commits con errores + IA deshabilitada: ~2 segundos

---

## Registro de Cambios en Documentación

_Se irá completando a medida que se tomen decisiones y se actualicen documentos_

### [Pendiente] Especificación de Agentes
- [ ] Agregar sección "Modelo de Distribución"
- [ ] Agregar sección "Integración en Proyectos"
- [ ] Unificar rutas de configuración
- [ ] Clarificar alcance de IA por agente

### [Pendiente] Guía de Implementación
- [ ] Reescribir Fase 1 con modelo de distribución elegido
- [ ] Actualizar ejemplos de instalación
- [ ] Actualizar rutas de configuración
- [ ] Agregar ejemplos de integración en otros proyectos

### [Pendiente] Plan del Proyecto
- [ ] Actualizar roadmap según decisiones
- [ ] Ajustar criterios de éxito
- [ ] Actualizar estimaciones de esfuerzo

---

## Próximos Pasos

1. **Resolver Decisión #1** - Modelo de distribución
2. **Resolver Decisión #2** - Modelo de integración
3. **Resolver Decisión #3** - Estructura de configuración
4. **Resolver Decisión #4** - Nomenclatura
5. **Resolver Decisión #5** - Alcance de IA

Una vez resueltas todas las decisiones:
- Actualizar los 3 documentos principales
- Crear documentación de integración
- Validar consistencia entre todos los archivos

---

**Última actualización:** 2026-01-20
**Estado general:** 🔴 En definición de decisiones arquitectónicas
