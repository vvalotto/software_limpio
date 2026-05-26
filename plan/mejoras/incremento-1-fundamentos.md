# Incremento 1 — Fundamentos: Output por módulo + Toggles de checks

**Versión:** v0.4.0
**Prioridad:** Alta — base que heredan todos los incrementos siguientes
**Branch sugerido:** `mejora-incremento-1-fundamentos`

## Objetivo

Corregir el output de los tres agentes para que agrupe por módulo (.py) en lugar de por paquete, y dar al usuario control granular sobre qué checks/analyzers/métricas se ejecutan.

## Issues incluidos

### Output por módulo
- [ ] #53 — CodeGuard: agrupar output por módulo (.py)
- [ ] #56 — DesignReviewer: agrupar output por módulo (.py)

### Toggles de checks
- [ ] #60 — CodeGuard: habilitar/deshabilitar checks desde `[tool.codeguard.checks]`
- [ ] #61 — DesignReviewer: habilitar/deshabilitar analyzers desde `[tool.designreviewer.checks]`
- [ ] #62 — ArchitectAnalyst: habilitar/deshabilitar métricas desde `[tool.architectanalyst.checks]`

## Orden de implementación

1. **#53 + #56** en paralelo — mismo cambio en formatter de cada agente, independientes entre sí
2. **#60** — CodeGuard toggles (el más simple, ya tiene estructura parcial)
3. **#61** — DesignReviewer toggles
4. **#62** — ArchitectAnalyst toggles

## Dependencias

Ninguna dependencia externa. Este incremento no requiere ningún otro.

## Criterios de cierre del incremento

- [ ] Output texto de los tres agentes agrupa por archivo `.py`
- [ ] JSON de los tres agentes usa `by_module` en lugar de `by_package`
- [ ] `[tool.<agente>.checks]` funcional en los tres agentes
- [ ] Tests actualizados
- [ ] `ruff` y `mypy` limpios
- [ ] `pytest` completo verde (766+ tests)
