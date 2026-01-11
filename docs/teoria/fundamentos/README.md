# Fundamentos del Diseño Limpio

> *"El Diseño Limpio es el conjunto de principios fundamentales de estructuración del software —anteriores y superiores a cualquier paradigma— cuya adherencia puede verificarse objetivamente mediante métricas."*

---

## Los Seis Principios Universales

Estos principios son **agnósticos al paradigma**. Preceden a la orientación a objetos y aplican igualmente a:
- Programación Orientada a Objetos
- Programación Funcional
- Programación Estructurada
- Enfoques multiparadigma

### Origen Histórico

| Concepto | Autor(es) | Año | Contexto Original |
|----------|-----------|-----|-------------------|
| Modularidad | David Parnas | 1972 | Sistemas en general |
| Ocultamiento de Información | David Parnas | 1972 | Descomposición de sistemas |
| Cohesión | Larry Constantine | 1968 | FORTRAN, COBOL |
| Acoplamiento | Larry Constantine | 1968 | Structured Design |
| Separación de Concerns | Edsger Dijkstra | 1974 | Ensayo filosófico |
| Abstracción | Barbara Liskov | 1974 | Lenguajes en general |

---

## Los Principios

### 1. [Modularidad](01_modularidad.md)

**Pregunta guía:** *¿Cómo dividir el sistema en partes manejables?*

Dividir un sistema en partes independientes que se pueden desarrollar, probar y modificar por separado.

### 2. [Ocultamiento de Información](02_ocultamiento_informacion.md)

**Pregunta guía:** *¿Qué exponer y qué esconder de cada módulo?*

Cada módulo oculta sus decisiones internas y expone solo lo necesario para usarlo.

### 3. [Cohesión](03_cohesion.md)

**Pregunta guía:** *¿Qué tan enfocado está cada módulo en una responsabilidad?*

Los elementos dentro de un módulo deben estar relacionados entre sí y trabajar hacia un propósito común.

### 4. [Acoplamiento](04_acoplamiento.md)

**Pregunta guía:** *¿Qué tan independientes son los módulos entre sí?*

El grado en que un módulo depende de otros. Bajo acoplamiento permite cambiar, probar y reusar módulos de forma independiente.

### 5. [Separación de Concerns](05_separacion_concerns.md)

**Pregunta guía:** *¿Cada módulo aborda un solo aspecto del problema?*

Dividir un programa de modo que cada parte aborde una preocupación (concern) distinta.

### 6. [Abstracción](06_abstraccion.md)

**Pregunta guía:** *¿Se separa el qué (comportamiento) del cómo (implementación)?*

Definir interfaces que describen qué hace un componente sin revelar cómo lo hace.

---

## Relación con SOLID

SOLID es una **reinterpretación** de estos fundamentos para el paradigma orientado a objetos:

```
FUNDAMENTOS (universal, agnóstico)
        │
        └── En OO: SOLID, GRASP, métricas CK
              │
              ├── SRP ← Cohesión + Separación de Concerns
              ├── OCP ← Abstracción + Ocultamiento
              ├── LSP ← Abstracción
              ├── ISP ← Cohesión + Modularidad
              └── DIP ← Acoplamiento + Abstracción
```

---

## Verificación con Métricas

| Principio | Métricas Asociadas | Herramientas |
|-----------|-------------------|--------------|
| Cohesión | LCOM, TCC, LCC | pylint, radon |
| Acoplamiento | CBO, Ca, Ce, Fan-In/Out | pydeps, pylint |
| Modularidad | LOC por módulo, dependencias | cloc, pydeps |
| Abstracción | I, A, D (Robert Martin) | pydeps + custom |
| Complejidad | CC, Cognitive Complexity | radon, flake8 |

---

## Lecturas Recomendadas

1. **Parnas, D.L. (1972)**. *On the Criteria to Be Used in Decomposing Systems into Modules*. Communications of the ACM.
2. **Constantine, L. & Yourdon, E. (1979)**. *Structured Design: Fundamentals of a Discipline of Computer Program and Systems Design*.
3. **Dijkstra, E.W. (1974)**. *On the Role of Scientific Thought*. EWD447.

---

[← Volver a Teoría](../README.md)
