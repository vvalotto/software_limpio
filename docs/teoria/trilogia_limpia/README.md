# La Trilogía Limpia

> *Un Enfoque Ético del Desarrollo de Software en la Era de la IA*

---

## El Vacío Conceptual

Robert Martin construyó una trilogía que se convirtió en referencia de la industria:

| Obra | Año | Nivel | Foco |
|------|-----|-------|------|
| Clean Code | 2008 | Micro | Funciones, nombres, estilo |
| Clean Coder | 2011 | Profesional | Ética y responsabilidad |
| Clean Architecture | 2017 | Macro | Componentes, capas, dependencias |

**El vacío:** No existe un tratamiento sistemático del nivel intermedio —el diseño de módulos, clases, responsabilidades y colaboraciones— bajo la etiqueta de "Diseño Limpio".

Este proyecto propone llenar ese vacío.

---

## La Estructura Tripartita

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA LIMPIA                          │
│              (componentes, capas, dependencias)                 │
│                   Nivel Macro - Sistema                         │
├─────────────────────────────────────────────────────────────────┤
│                      DISEÑO LIMPIO                              │
│           (módulos, cohesión, acoplamiento)                     │
│                Nivel Medio - Estructura                         │
├─────────────────────────────────────────────────────────────────┤
│                      CÓDIGO LIMPIO                              │
│              (funciones, nombres, estilo)                       │
│                 Nivel Micro - Expresión                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Contenidos

### [Código Limpio](codigo_limpio.md)

El nivel **micro**: la expresión clara de las ideas en código.

- Nombres significativos
- Funciones pequeñas
- Comentarios que agregan valor
- Formato consistente
- Manejo de errores

**Pregunta ética:** *¿Puede otro humano entender esto?*

### [Diseño Limpio](diseno_limpio.md)

El nivel **medio**: la estructura de módulos y sus relaciones.

- Los 6 principios fundamentales
- Cohesión y acoplamiento
- Responsabilidades claras
- Colaboraciones bien definidas

**Pregunta ética:** *¿Puede otro humano modificar esto?*

### [Arquitectura Limpia](arquitectura_limpia.md)

El nivel **macro**: la organización del sistema completo.

- Separación en capas
- Regla de dependencia
- Boundaries y políticas
- Casos de uso

**Pregunta ética:** *¿Puede el sistema evolucionar?*

---

## Responsabilidad en Cada Nivel

| Nivel | Ética | Responsabilidad |
|-------|-------|-----------------|
| Código | Comunicación | Respeto por quien lee |
| Diseño | Colaboración | Respeto por quien mantiene |
| Arquitectura | Sostenibilidad | Respeto por el futuro |

---

## Métricas por Nivel

| Nivel | Métricas Clave | Umbral |
|-------|----------------|--------|
| **Código** | CC (Complejidad Ciclomática) | ≤ 10 |
| | Líneas por función | ≤ 20 |
| | Profundidad de anidamiento | ≤ 4 |
| **Diseño** | LCOM (Cohesión) | ≤ 1 |
| | CBO (Acoplamiento) | ≤ 5 |
| | MI (Mantenibilidad) | > 20 |
| **Arquitectura** | D (Distance from Main Sequence) | ≈ 0 |
| | Violaciones de capa | = 0 |
| | Ciclos de dependencia | = 0 |

---

## Contribución Original

Este proyecto articula el **"Diseño Limpio"** como concepto independiente:

1. Agnóstico al paradigma
2. Basado en principios históricos (pre-OO)
3. Verificable mediante métricas
4. Complementario a la trilogía de Martin

---

[← Volver a Teoría](../README.md)
