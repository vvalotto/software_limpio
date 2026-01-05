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

## Contenido pendiente

- [ ] CodeGuard (implementación básica)
- [ ] DesignReviewer (con integración IA)
- [ ] ArchitectAnalyst (dashboard y tendencias)
- [ ] Configuraciones YAML
- [ ] Integración CI/CD
