# Guías de Usuario

Guías prácticas para usar los agentes de control de calidad.

---

## Agentes Disponibles

| Agente | Guía | Estado |
|--------|------|--------|
| CodeGuard | [codeguard.md](codeguard.md) | ✅ Disponible |
| DesignReviewer | designreviewer.md | 🚧 Próximamente |
| ArchitectAnalyst | architectanalyst.md | 🚧 Próximamente |

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

# DesignReviewer - Análisis de diseño (próximamente)
designreviewer

# ArchitectAnalyst - Análisis de arquitectura (próximamente)
architectanalyst
```

---

## Documentación Adicional

- [Especificación Técnica de Agentes](../agentes/especificacion_agentes_calidad.md)
- [Catálogo de Métricas](../metricas/Metricas_Clasificadas.md)
- [Teoría de Principios](../teoria/fundamentos/README.md)

---

[← Volver a Documentación](../README.md)
