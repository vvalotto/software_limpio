# Guías de Usuario

Guías prácticas para usar los agentes de control de calidad.

---

## Agentes Disponibles

| Agente | Guía de Usuario | Guía de Adopción |
|--------|----------------|-----------------|
| CodeGuard | [codeguard.md](codeguard.md) | [adopcion-codeguard.md](adopcion-codeguard.md) |
| DesignReviewer | [designreviewer.md](designreviewer.md) | [adopcion-designreviewer.md](adopcion-designreviewer.md) |
| ArchitectAnalyst | [architectanalyst.md](architectanalyst.md) | [adopcion-architectanalyst.md](adopcion-architectanalyst.md) |

---

## Inicio Rápido

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/vvalotto/software_limpio.git
cd software_limpio

# Crear entorno virtual
python3.11 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar en modo desarrollo
pip install -e ".[dev]"
```

### Uso Básico

```bash
# CodeGuard - Análisis rápido pre-commit
codeguard .

# DesignReviewer - Análisis de diseño (bloquea si hay CRITICAL)
designreviewer src/

# ArchitectAnalyst - Análisis de arquitectura (solo informa)
architectanalyst src/
```

---

## Documentación Adicional

- [Especificación Técnica de Agentes](../agentes/especificacion_agentes_calidad.md)
- [Catálogo de Métricas](../metricas/Metricas_Clasificadas.md)
- [Teoría de Principios](../teoria/fundamentos/README.md)

---

[← Volver a Documentación](../README.md)
