# Software Limpio — Propuesta de Formación Corporativa

**Facultad de Ingeniería · Programa de Extensión Universitaria**

---

## El problema que sus equipos ya tienen

La productividad de desarrollo aumentó. La calidad del código, no.

El reporte DORA 2024 lo midió: los equipos que adoptaron herramientas de IA generativa
reportaron un 5% de aumento en velocidad de entrega y un 7,2% de caída en la estabilidad
de sus sistemas. Más código en menos tiempo, pero más deuda técnica, más bugs en producción,
más tiempo perdido en mantenimiento.

El problema no es la herramienta. Es que nadie formó a los desarrolladores para el rol que
ahora necesitan cumplir: **evaluar calidad, no solo producir código**.

Cuando cualquier desarrollador puede generar 200 líneas de código funcional en minutos, la
pregunta que importa dejó de ser "¿funciona?" y pasó a ser "¿está bien construido?".
Responder esa pregunta requiere criterio, principios y métricas. No intuición.

---

## La propuesta

**Software Limpio** es un programa de formación en calidad de software diseñado para equipos
de desarrollo profesional. Combina fundamentos teóricos sólidos, métricas objetivas y
herramientas de análisis automatizado para que los desarrolladores puedan evaluar —y mejorar—
la calidad de su propio código y el de sus equipos.

El programa es desarrollado y dictado por la Facultad, con respaldo en investigación aplicada
y una herramienta open source construida específicamente para este propósito: **quality-agents**.

---

## ¿Qué aprenden los participantes?

El programa cubre tres niveles de calidad, cada uno con sus principios, sus métricas y sus
herramientas de verificación:

### Nivel 1 — Código Limpio
*¿Puede este código ser leído por otro desarrollador?*

- Principios de legibilidad, nombrado y estructura a nivel función
- Complejidad ciclomática y cognitiva: qué miden y cómo interpretarlas
- Estilo, documentación y estándares (PEP8, type hints)
- Herramienta: **CodeGuard** — análisis automático en menos de 5 segundos

### Nivel 2 — Diseño Limpio
*¿Puede este módulo ser modificado sin efecto dominó?*

- Cohesión y acoplamiento: los dos conceptos que más impactan el mantenimiento
- SOLID en la práctica: no como reglas, sino como consecuencias de principios
- Code smells: cómo reconocer señales de diseño deteriorado
- Métricas: CBO, LCOM, WMC, DIT y cuándo actuar sobre ellas
- Herramienta: **DesignReviewer** — análisis automático en cada Pull Request

### Nivel 3 — Arquitectura Limpia
*¿Puede este sistema evolucionar sin reescribirse?*

- Métricas de Martin: estabilidad, abstracción y la zona de la muerte
- Ciclos de dependencia: por qué son tan costosos y cómo detectarlos
- Violaciones de capas: cómo una dependencia mal puesta destruye la arquitectura
- Tendencias históricas: observar cómo evoluciona la salud arquitectónica sprint a sprint
- Herramienta: **ArchitectAnalyst** — análisis al fin de cada sprint

---

## Lo que distingue este programa

**No es solo teoría.** Cada concepto tiene una métrica que lo mide y una herramienta que lo
verifica. Los participantes salen con criterio *y* con instrumentos para aplicarlo el día siguiente.

**No es solo herramienta.** Las herramientas de análisis estático existen hace años. Lo que
falta en los equipos es el marco conceptual para interpretar los resultados y tomar decisiones
fundamentadas. Este programa cubre ambos lados.

**Cubre el nivel que nadie sistematizó.** La literatura clásica tiene "Código Limpio" (Martin)
y "Arquitectura Limpia" (Martin). El nivel de diseño — módulos, clases, relaciones — nunca
recibió el mismo tratamiento sistemático. Este programa llena ese vacío con métricas concretas
y criterios objetivos.

**Está en español, pensado para la región.** No es una traducción de material anglosajón.
Es contenido original, con ejemplos y contexto apropiados para equipos latinoamericanos.

**Incluye el paradigma IA.** El programa aborda explícitamente cómo cambia el rol del
desarrollador cuando la IA genera código: de productor a evaluador. Los participantes entienden
qué competencias construir para ser más valiosos, no menos, en ese contexto.

---

## ¿Para quién es?

El programa está diseñado para:

- **Desarrolladores con 2+ años de experiencia** que quieren formalizar y profundizar su criterio técnico
- **Tech leads y arquitectos** que necesitan lenguaje común y métricas objetivas para guiar a sus equipos
- **Engineering managers** que quieren entender la calidad técnica sin adentrarse en el código

No es un curso introductorio de programación. Requiere experiencia previa en desarrollo de software.

---

## Formato

| | |
|---|---|
| **Duración** | 32 horas (8 módulos de 4 horas) |
| **Modalidad** | Presencial o virtual sincrónica |
| **Frecuencia** | Semanal (2 meses) o intensivo (1 semana) |
| **Grupo** | 12 a 20 participantes |
| **Requisitos técnicos** | Python 3.11+, acceso a repositorio de código propio (para ejercicios) |

Cada módulo combina exposición conceptual (40%), análisis de casos (30%) y trabajo práctico
sobre código real del equipo (30%).

---

## Resultados esperados

Al finalizar el programa, los equipos tienen:

- **Vocabulario técnico compartido** para discutir calidad sin ambigüedad
- **Métricas objetivas** integradas en el proceso de revisión de código y de Pull Requests
- **Herramientas instaladas y configuradas** en su pipeline de desarrollo
- **Criterio propio** para tomar decisiones de refactorización fundamentadas en datos

El impacto medible se observa en ciclos de 30 a 90 días: reducción de tiempo en code review,
menos regresiones en producción, y mayor velocidad de incorporación de desarrolladores nuevos.

---

## Respaldo académico

El programa es desarrollado en el marco de la Facultad de Ingeniería, con base en investigación
aplicada sobre métricas de calidad de software y prácticas de ingeniería de software modernas.

El material teórico se fundamenta en la literatura clásica del área (Parnas, Constantine,
Dijkstra, Martin, Fowler) y en investigación reciente sobre el impacto de la IA en el desarrollo
profesional (DORA Report, GitHub Research, estudios de Peng et al.).

La herramienta **quality-agents** es open source, disponible en GitHub, con más de 766 tests
automatizados que garantizan su correcto funcionamiento.

---

## Próximos pasos

Para coordinar una propuesta adaptada a las necesidades específicas de su equipo:

- Tamaño y perfil del grupo
- Nivel de experiencia predominante
- Stack tecnológico (el programa es agnóstico, los ejemplos se adaptan)
- Objetivos concretos de mejora

**Contacto:** [datos de contacto de la Facultad]

---

*Software Limpio es un programa de extensión universitaria. El material, las herramientas
y la metodología son desarrollados y mantenidos por el equipo de la Facultad.*
