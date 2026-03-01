# Agentes de Control de Calidad

Sistema de control de calidad en tres niveles.

## Arquitectura

```
Pre-commit (seg)     Review (min)        Sprint-end (horas)
     ↓                    ↓                     ↓
  CodeGuard    →   DesignReviewer   →   ArchitectAnalyst
     │                    │                     │
  ADVERTIR             BLOQUEAR              ANALIZAR
```

## Agentes

| Agente | Momento | Acción | Tiempo |
|--------|---------|--------|--------|
| CodeGuard | Pre-commit | Advierte (no bloquea) | < 5s |
| DesignReviewer | Review/PR | Bloquea si crítico | 2-5 min |
| ArchitectAnalyst | Fin de sprint | Analiza tendencias | 10-30 min |

## Implementado

| Agente | Versión | Estado | Guía |
|--------|---------|--------|------|
| CodeGuard | v0.1.0 | ✅ Completo | `docs/guias/codeguard.md` |
| DesignReviewer | v0.2.0 | ✅ Completo (sin IA) | `docs/guias/designreviewer.md` |
| ArchitectAnalyst | v0.3.0 | ✅ Completo (sin IA, sin dashboard) | `docs/guias/architectanalyst.md` |

## Pendiente

- [ ] Integración IA opt-in (CodeGuard, DesignReviewer, ArchitectAnalyst)
- [ ] Publicación en PyPI (`pip install quality-agents`)
- [ ] GitHub Actions CI/CD
