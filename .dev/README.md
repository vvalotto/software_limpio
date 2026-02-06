# 🔧 .dev - Archivos de Desarrollo

> Documentación y contexto para contribuidores y desarrollo del proyecto

---

## 📋 Contenido

| Archivo | Descripción |
|---------|-------------|
| **CLAUDE.md** | Instrucciones para Claude Code - Guía técnica del proyecto |
| **SESION.md** | Contexto de sesión - Estado actual, progreso, próximas tareas |
| **plan/** | Planificación del proyecto y roadmap |

---

## 🤖 Para Claude Code

Los comandos personalizados de Claude Code (`/sesion`, `/guardar-sesion`) usan archivos de esta carpeta:

```bash
# Cargar contexto de sesión
/sesion
# → Lee .dev/SESION.md

# Guardar progreso
/guardar-sesion
# → Actualiza .dev/SESION.md
```

---

## 📝 SESION.md

**Propósito:** Mantener contexto entre sesiones de desarrollo.

**Contiene:**
- Estado actual del proyecto (branch, commits, progreso)
- Tareas completadas, en progreso y pendientes
- Decisiones arquitectónicas tomadas
- Notas para la próxima sesión

**Cuándo actualizar:** Al final de cada sesión de desarrollo (usar `/guardar-sesion`)

---

## 📖 CLAUDE.md

**Propósito:** Guía técnica para Claude Code al trabajar en este proyecto.

**Contiene:**
- Overview del proyecto
- Comandos de desarrollo
- Arquitectura del sistema
- Decisiones técnicas
- Referencias a documentación clave

**Cuándo actualizar:**
- Cambios en arquitectura
- Nuevas decisiones técnicas importantes
- Cambios en estructura del proyecto
- Actualización de comandos/workflows

---

## 📋 plan/

**Propósito:** Planificación detallada del proyecto.

**Contiene:**
- `plan_proyecto.md` - Plan maestro del proyecto
- Roadmap de desarrollo
- Estimaciones de tiempo
- Fases y tickets

**Cuándo actualizar:**
- Completar una fase
- Ajustar estimaciones
- Redefinir prioridades

---

## 🚫 No Incluir en Distribución

Los archivos de esta carpeta son para desarrollo interno. No se incluyen en el paquete distribuible en PyPI (solo opcionalmente en MANIFEST.in para contribuidores).

---

## 🤝 Para Contribuidores

Si estás contribuyendo al proyecto:

1. **Lee primero:** `.dev/SESION.md` para entender el estado actual
2. **Consulta:** `.dev/CLAUDE.md` para decisiones técnicas
3. **Revisa:** `.dev/plan/` para ver roadmap y prioridades
4. **Actualiza:** `.dev/SESION.md` al finalizar tu trabajo

---

**Software Limpio** - Control de Calidad Automatizado para Python 🚀
