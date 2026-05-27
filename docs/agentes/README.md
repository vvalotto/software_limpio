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
| CodeGuard | v0.4.0 | ✅ 9 checks, toggles, output por módulo | `docs/guias/codeguard.md` |
| DesignReviewer | v0.4.0 | ✅ 14 analyzers, toggles, output por módulo | `docs/guias/designreviewer.md` |
| ArchitectAnalyst | v0.4.0 | ✅ 10 métricas, toggles, analysis_depth, layer_roles | `docs/guias/architectanalyst.md` |

## Pendiente

- [ ] Wiring IA opt-in (infraestructura lista en v0.4.0)
- [ ] Publicación en PyPI (`pip install quality-agents`)
- [ ] GitHub Actions CI/CD
