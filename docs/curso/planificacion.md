# Planificación — Software Limpio · Curso Corporativo

---

## Parte A — Elaboración del Material

### Diagnóstico de partida

El proyecto tiene una base sólida pero incompleta para un curso:

| Componente | Estado | Brecha |
|---|---|---|
| Teoría (fundamentos, trilogía, paradigma) | ✅ Existe | Escrita como referencia, no como pedagogía |
| Métricas (catálogo completo) | ✅ Existe | Sin ejercicios ni casos prácticos |
| Guías de usuario (3 agentes) | ✅ Existe | Orientadas al uso, no al aprendizaje |
| Herramientas (CodeGuard, DR, AA) | ✅ Funcionan | sample_project solo cubre CodeGuard |
| Progresión didáctica | ❌ No existe | Falta el hilo conductor teoría → métrica → herramienta |
| Ejercicios y actividades | ❌ No existe | Ningún archivo contiene ejercicios |
| Material "antes/después" | ❌ No existe | No hay ejemplos de refactorización didáctica |
| Evaluaciones | ❌ No existe | Sin rúbricas ni criterios de evaluación |

El trabajo de elaboración no es escribir desde cero: es **transformar y completar** lo que existe.

---

### Fases de Elaboración

#### Fase 1 — Diseño Pedagógico (3 semanas)

Antes de escribir una línea de contenido, definir la arquitectura del curso:

- Objetivos de aprendizaje por módulo (qué debe saber y poder hacer el participante al terminar)
- Secuencia de contenidos y dependencias entre módulos
- Criterios de evaluación (qué evidencia demuestra que el objetivo se alcanzó)
- Formato de cada clase: proporción teoría / análisis de casos / práctica
- Perfil de participante objetivo y conocimientos previos requeridos

**Entregable:** Documento de diseño instruccional con estructura completa del curso.

---

#### Fase 2 — Expansión del Material Teórico (5 semanas)

Los archivos de `docs/teoria/` son el esqueleto. Cada uno necesita transformarse en
contenido de clase: más largo, con ejemplos concretos, con preguntas que guíen la
reflexión y con conexión explícita hacia las métricas y las herramientas.

Temas a desarrollar, en orden de prioridad:

1. **El Nuevo Paradigma** — Por qué cambia el rol del desarrollador con la IA. Es el
   módulo de apertura y necesita impacto: datos, casos reales, la paradoja DORA explicada
   en términos que una empresa entienda.

2. **Los 6 Fundamentos Universales** — Modularidad, cohesión, acoplamiento, ocultamiento,
   separación de concerns, abstracción. Cada uno necesita: definición precisa, ejemplo de
   código que lo viola, ejemplo que lo respeta, y la métrica que lo mide.

3. **Trilogía Limpia** — Los tres niveles con sus preguntas clave. Énfasis especial en el
   nivel de Diseño (el original), que necesita más desarrollo que los otros dos porque no
   tiene referencia externa directa.

4. **Marco Filosófico** — Las cuatro virtudes y la dimensión ética. Más corto, pensado como
   apertura o cierre de módulo, no como bloque independiente.

**Entregable:** Contenido expandido para cada módulo (~2.000-3.000 palabras por módulo,
con ejemplos de código y conexiones a métricas).

---

#### Fase 3 — Creación de Ejercicios Prácticos (4 semanas)

La parte más importante y la que más trabajo lleva. Cada módulo necesita:

- **Código con problemas intencionales:** archivos Python que violen los principios del
  módulo de manera clara y didáctica (diferente al sample_project actual, que fue diseñado
  para testing de las herramientas, no para aprendizaje).
- **Guía de análisis:** qué buscar, cómo interpretarlo, qué métricas observar.
- **Solución comentada:** la versión refactorizada con explicación de cada decisión.
- **Ejercicio de aplicación:** código del participante o caso provisto para analizar
  con las herramientas y proponer mejoras.

Esto incluye expandir `examples/sample_project/` para cubrir DesignReviewer y
ArchitectAnalyst (ya registrado en el backlog).

**Entregable:** Repositorio de ejercicios con código problema, guía de análisis y solución
para cada módulo.

---

#### Fase 4 — Material de Evaluación (2 semanas)

- Cuestionarios de comprensión por módulo (no memorización: comprensión y aplicación)
- Proyecto integrador final: análisis completo de un repositorio real con los tres agentes,
  con informe de hallazgos y plan de mejora
- Rúbrica de evaluación del proyecto integrador
- Criterios de aprobación

**Entregable:** Set completo de evaluaciones con rúbricas.

---

#### Fase 5 — Piloto Interno (4 semanas)

Dictar el curso completo una vez, con un grupo reducido (5-8 personas, idealmente mixto:
desarrolladores + un tech lead). Objetivo: validar tiempos, detectar lagunas y puntos de
confusión, calibrar dificultad de ejercicios.

**Entregable:** Curso completo dictado + feedback sistematizado + lista de ajustes.

---

#### Fase 6 — Revisión Post-Piloto (2 semanas)

Incorporar los ajustes del piloto. Afinar los ejercicios que resultaron confusos. Corregir
estimaciones de tiempo por módulo. Preparar versión final.

**Entregable:** Material de curso en versión 1.0, listo para dictar a empresas.

---

### Cronograma de Elaboración

```
Mes 1        Mes 2        Mes 3        Mes 4        Mes 5
├── F1 ──┤
          ├──── F2 ────┤
                        ├─── F3 ───┤
                                    ├─ F4 ─┤
                                            ├── F5 (piloto) ──┤
                                                               ├ F6 ┤
```

**Duración total estimada:** 5 meses (trabajo a tiempo parcial, ~10-15 horas semanales)

---

---

## Parte B — El Curso

### Estructura General

**Nombre:** Software Limpio — Control de Calidad en la Era de la IA
**Duración:** 32 horas (8 módulos de 4 horas)
**Formato:** Semanal (2 meses) o intensivo (4 días de 8 horas)
**Participantes:** 12-20 desarrolladores con 2+ años de experiencia

Cada módulo sigue la misma estructura interna:
- **Apertura** (20 min): pregunta o caso que instala el problema
- **Conceptos** (60 min): teoría con ejemplos de código
- **Demostración** (40 min): uso de la herramienta sobre código real
- **Práctica** (60 min): trabajo del participante sobre ejercicio provisto
- **Cierre** (20 min): síntesis, conexión con el módulo siguiente, tarea

---

### Módulo 1 — El Nuevo Paradigma (4 hs)

*Pregunta central: ¿Qué le pasa al valor de un desarrollador cuando la IA escribe código?*

**Contenidos:**
- La paradoja DORA: más velocidad, menos estabilidad
- El cambio de rol: de productor a evaluador
- Las cuatro competencias del nuevo paradigma: Dirigir, Evaluar, Refinar, Decidir
- El triángulo Principios ↔ Métricas ↔ IA
- Presentación del framework Software Limpio y sus tres niveles

**Herramienta:** Instalación y primer uso de `quality-agents`

**Tarea:** Correr `codeguard` sobre el repositorio propio del participante. Traer resultados al módulo 2.

---

### Módulo 2 — Fundamentos Universales (4 hs)

*Pregunta central: ¿Por qué algunos principios llevan 50 años vigentes?*

**Contenidos:**
- Los 6 principios universales: Modularidad, Ocultamiento de Información, Cohesión,
  Acoplamiento, Separación de Concerns, Abstracción
- Origen histórico y por qué siguen siendo válidos
- SOLID como consecuencia, no como punto de partida
- Relación entre principios y métricas: cada principio tiene un número

**Sin herramienta específica** — módulo conceptual, base para todo lo que sigue

**Tarea:** Identificar en el repositorio propio un ejemplo claro de violación a cohesión o acoplamiento.

---

### Módulo 3 — Código Limpio (4 hs)

*Pregunta central: ¿Puede este código ser leído por alguien que no lo escribió?*

**Contenidos:**
- Métricas de código: Complejidad Ciclomática, Complejidad Cognitiva, LOC, Nesting Depth
- Cómo interpretar los resultados: umbrales, falsos positivos, decisiones
- Estilo, nombrado y documentación: PEP8, type hints, docstrings
- Cuándo refactorizar vs. cuándo aceptar la deuda

**Herramienta:** **CodeGuard** — análisis pre-commit, integración con Git

**Práctica:** Analizar código con problemas intencionales, identificar los tres issues más importantes y proponer refactorización.

**Tarea:** Configurar CodeGuard en el repositorio propio con umbrales acordados por el equipo.

---

### Módulo 4 — Diseño Limpio I: Cohesión y Acoplamiento (4 hs)

*Pregunta central: ¿Puede este módulo ser modificado sin efecto dominó?*

**Contenidos:**
- LCOM: qué mide la cohesión y por qué importa
- CBO y Fan-Out: el costo real del acoplamiento
- Imports circulares: cómo se forman y por qué son tan costosos
- La diferencia entre acoplamiento inevitable y acoplamiento evitable

**Herramienta:** **DesignReviewer** — primeros análisis, interpretación de BLOCKING ISSUES

**Práctica:** Analizar módulo con baja cohesión. Proponer split de responsabilidades.

---

### Módulo 5 — Diseño Limpio II: Herencia, Complejidad y Code Smells (4 hs)

*Pregunta central: ¿Cómo reconozco que el diseño se está deteriorando?*

**Contenidos:**
- WMC, DIT, NOP: métricas de herencia y complejidad por clase
- Los code smells como señales tempranas: God Object, Long Method, Feature Envy,
  Data Clumps, Long Parameter List
- Mapeo a violaciones SOLID: cada smell tiene un principio que viola
- Estrategia de adopción: umbrales permisivos al principio, ajuste gradual

**Herramienta:** **DesignReviewer** — análisis completo, JSON output para CI/CD

**Práctica:** Análisis completo de un módulo real. Priorización de hallazgos por impacto.

**Tarea:** Configurar DesignReviewer en el pipeline de Pull Requests del equipo.

---

### Módulo 6 — Arquitectura Limpia I: Métricas de Martin (4 hs)

*Pregunta central: ¿Qué tan estable es la base sobre la que construimos?*

**Contenidos:**
- Estabilidad (I) y Abstracción (A): qué miden y cómo se relacionan
- La Distancia de la Secuencia Principal (D): la zona de la muerte y la zona inútil
- Acoplamiento aferente y eferente (Ca, Ce): quién depende de quién
- Cómo leer el grafo de dependencias de un proyecto real

**Herramienta:** **ArchitectAnalyst** — primer análisis, interpretación de métricas de Martin

**Práctica:** Analizar la arquitectura de un proyecto Python conocido. Identificar el componente más frágil.

---

### Módulo 7 — Arquitectura Limpia II: Ciclos, Capas y Tendencias (4 hs)

*Pregunta central: ¿Cómo sé si la arquitectura está mejorando o deteriorándose?*

**Contenidos:**
- Ciclos de dependencia: el algoritmo de Tarjan explicado sin matemática
- Violaciones de capas: cómo una dependencia incorrecta destruye la arquitectura limpia
- Tendencias históricas: el valor de comparar sprint a sprint (↑ ↓ =)
- ArchitectAnalyst como herramienta de observabilidad, no de bloqueo

**Herramienta:** **ArchitectAnalyst** — análisis histórico con sprint_id, comparación de tendencias

**Práctica:** Simulación de análisis multi-sprint. Interpretación de tendencias de degradación.

**Tarea:** Programar ArchitectAnalyst para correr automáticamente al final de cada sprint.

---

### Módulo 8 — Integración y Adopción (4 hs)

*Pregunta central: ¿Cómo integramos esto en el trabajo real del equipo?*

**Contenidos:**
- El pipeline completo: pre-commit → PR review → fin de sprint
- Estrategia de adopción: proyecto existente vs. proyecto nuevo
- Cómo definir umbrales que el equipo acepte y entienda
- Gestión del cambio: cómo presentar métricas sin generar resistencia
- La IA como capa siguiente: hacia dónde va el framework (v0.4.0)

**Herramienta:** Los tres agentes integrados

**Proyecto integrador:** Análisis completo de un repositorio real con los tres agentes.
Informe de hallazgos, priorización y plan de mejora a 90 días.

---

### Evaluación

| Instancia | Peso | Descripción |
|---|---|---|
| Participación y tareas semanales | 30% | Aplicación de cada herramienta en repositorio propio |
| Ejercicios prácticos en clase | 30% | Análisis y refactorización de código provisto |
| Proyecto integrador final | 40% | Análisis completo + informe + plan de mejora |

**Aprobación:** 60% del total. Certificado emitido por la Facultad.

---

### Materiales incluidos

- Acceso al repositorio del curso (ejercicios, soluciones, código de ejemplo)
- Licencia de uso de `quality-agents` (open source, sin costo)
- Documentación completa en español
- Guías de adopción para los tres agentes
- Soporte por consultas durante 30 días post-curso

---

### Variante intensiva (4 días)

Para empresas que prefieren formato concentrado:

| Día | Módulos | Foco |
|---|---|---|
| Día 1 | 1 + 2 | Paradigma + Fundamentos |
| Día 2 | 3 + 4 | Código Limpio + Diseño I |
| Día 3 | 5 + 6 | Diseño II + Arquitectura I |
| Día 4 | 7 + 8 | Arquitectura II + Integración |

En formato intensivo se reduce el tiempo de tareas inter-módulo. El proyecto integrador
se entrega en los 15 días siguientes al curso.
