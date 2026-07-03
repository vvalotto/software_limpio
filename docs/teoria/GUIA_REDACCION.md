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

## Formato Ensayo Filosófico

Para `marco_filosofico/` y `nuevo_paradigma/`, donde el contenido es más conceptual y argumentativo que los principios de `fundamentos/`.

- **Extensión objetivo**: 200-250 líneas. Si un archivo supera este rango, dividirlo o recortar redundancia antes de sumar contenido nuevo.
- **Tablas resumen compartidas**: si un concepto (por ejemplo, una comparación por niveles Código/Diseño/Arquitectura) ya está desarrollado en profundidad en un archivo, los demás archivos que lo mencionen deben **linkear a esa sección** en vez de repetir la tabla completa. La tabla vive en un solo lugar: el archivo que define el concepto en profundidad (no el README de la carpeta).
- **Métricas/Anti-patrones obligatorias**: todo ensayo debe cerrar con una sección breve (no exhaustiva) de Métricas o Anti-patrones que conecte la reflexión filosófica con algo verificable en código, diseño o arquitectura. No hace falta la profundidad de `fundamentos/`, pero no puede faltar — es lo que sostiene la promesa de "verificación objetiva" del proyecto.

### Plantilla para Ensayo Filosófico

```markdown
# [Concepto]

> Cita o autor de referencia

**Pregunta guía:** *¿...?*

---

## Definición
Qué es, en pocos párrafos.

## Por qué importa
El problema o tensión que aborda.

## Desarrollo
El argumento central. Puede tener subsecciones (`###`), pero sin extenderse en variaciones redundantes del mismo punto.

## En los Tres Niveles
Tabla breve Código/Diseño/Arquitectura (solo si este archivo es el dueño del concepto; si no, linkear al archivo que la tiene).

## Métricas / Anti-patrones
Sección breve: cómo se verifica o qué señales delatan su ausencia.

---

[← Volver](README.md)
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

*Última actualización: Julio 2026*
