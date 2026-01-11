# Guía de Redacción - Teoría

> **Instrucción para Claude:** Leer este archivo antes de redactar contenido en `docs/teoria/`.

---

## Estilo de Escritura

- **Conciso**: Ir al punto, sin rodeos
- **Simple**: Preferir palabras comunes sobre jerga técnica
- **Directo**: Voz activa, oraciones cortas
- **Accesible**: Técnico pero no académico

### Evitar

- Oraciones largas con múltiples subordinadas
- Jerga innecesaria cuando hay alternativas claras
- Repetición de conceptos
- Explicaciones redundantes

### Preferir

- Una idea por párrafo
- Ejemplos concretos sobre definiciones abstractas
- Tablas para comparaciones
- Código para ilustrar conceptos

---

## Estructura de Archivos

Cada archivo es una **sección** con subsecciones:

```markdown
# Título Principal

> Cita o frase clave (opcional)

---

## Definición
Qué es, en 2-3 oraciones.

## Por qué importa
El problema que resuelve.

## Cómo se aplica
Ejemplos prácticos.

## Métricas asociadas
Cómo verificarlo objetivamente.

---

[← Volver](README.md)
```

---

## Principios Fundamentales: Los 3 Niveles

Para cada principio en `fundamentos/`, mostrar su aplicación en:

| Nivel | Pregunta | Ejemplo |
|-------|----------|---------|
| **Código** | ¿Cómo afecta a funciones y clases? | Funciones pequeñas, nombres claros |
| **Diseño** | ¿Cómo afecta a módulos y sus relaciones? | Cohesión alta, acoplamiento bajo |
| **Arquitectura** | ¿Cómo afecta al sistema completo? | Capas, boundaries, dependencias |

### Plantilla para Principios

```markdown
# [Nombre del Principio]

> Autor, Año

**Pregunta guía:** *¿...?*

---

## Definición

## En Código
Cómo se manifiesta a nivel de funciones y clases.

## En Diseño
Cómo se manifiesta a nivel de módulos.

## En Arquitectura
Cómo se manifiesta a nivel de sistema.

## Métricas

## Anti-patrones
Qué pasa cuando se viola.

## Ejemplo

---

[← Volver a Fundamentos](README.md)
```

---

## Formato

- **Títulos**: Usar `#`, `##`, `###` jerárquicamente
- **Énfasis**: `**negrita**` para conceptos clave, `*cursiva*` para términos técnicos
- **Código**: Bloques con ` ``` ` para ejemplos
- **Tablas**: Para comparaciones y resúmenes
- **Listas**: Para enumeraciones, preferir bullet points

---

## Idioma

- Español rioplatense (vos, ustedes)
- Términos técnicos en inglés cuando son estándar (refactoring, code smell, etc.)
- Sin emojis salvo en navegación (← →)

---

*Última actualización: Enero 2025*
