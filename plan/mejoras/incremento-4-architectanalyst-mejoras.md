# Incremento 4 — ArchitectAnalyst arquitectura-aware + nuevas métricas

**Versión:** v0.4.0
**Prioridad:** Media-Alta (alto impacto en proyectos hexagonal/CQRS)
**Requiere:** Incremento 1 completo
**Branch sugerido:** `mejora-incremento-4-architectanalyst`

## Objetivo

Hacer que ArchitectAnalyst sea consciente del contexto arquitectural (roles de capa, profundidad de análisis) y agregar las métricas faltantes de la suite de Martin más detección de god packages y cobertura.

## Issues incluidos

### Calibración de métricas existentes
- [ ] #47 — InstabilityAnalyzer + `layer_roles` para CQRS/ES
- [ ] #48 — DistanceAnalyzer + `analysis_depth` para hexagonal

### Nuevas métricas
- [ ] #57 — RelationalCohesionAnalyzer — métrica H de Martin
- [ ] #58 — GodPackageAnalyzer — paquetes con demasiada concentración
- [ ] #49 — CoverageAnalyzer — cobertura de tests en el reporte

## Orden de implementación

1. **#47 layer_roles** — requiere cambio en config + InstabilityAnalyzer. Base para calibración arquitectural.
2. **#48 analysis_depth** — cambio en config + DistanceAnalyzer. Independiente de #47.
3. **#57 RelationalCohesionAnalyzer** — nueva métrica, usa DependencyGraph existente.
4. **#58 GodPackageAnalyzer** — nueva métrica, usa DependencyGraph + conteo de clases existente.
5. **#49 CoverageAnalyzer** — independiente, lee `coverage.json`.

## Notas de diseño

**#47 — layer_roles:**
- Agregar `layer_roles: Dict[str, str]` a `ArchitectAnalystConfig` (glob → "leaf" | "stable")
- En `InstabilityAnalyzer`: para cada módulo, verificar match contra patrones glob
  - `leaf`: warn si I < (1 − max_instability) — algo depende de una hoja, flujo roto
  - `stable`: warn si I > max_instability — comportamiento actual
- Sin match: comportamiento actual sin cambios

**#48 — analysis_depth:**
- Agregar `analysis_depth: int = 1` a `ArchitectAnalystConfig`
- En `DistanceAnalyzer._aggregate_to_packages()`: cambiar `module.split(".")[0]` por `".".join(module.split(".")[:depth])`
- Con depth=1: idéntico al comportamiento actual

**#57 — RelationalCohesionAnalyzer:**
- H = (R + 1) / N donde R = relaciones internas del paquete, N = tipos en el paquete
- Usa `DependencyGraph` existente para contar relaciones internas

**#58 — GodPackageAnalyzer:**
- Por tamaño: paquetes con más de `max_package_classes` clases
- Por Ca: paquetes con Ca > `max_package_ca`
- Reutiliza lógica de conteo de `DistanceAnalyzer`

**#49 — CoverageAnalyzer:**
- Busca `coverage.json` en path configurable
- Parsea `totals.percent_covered`
- WARNING si < `min_coverage` (default: 80%)
- WARNING si no encuentra el archivo

## Cambios en config requeridos

```toml
[tool.architectanalyst]
analysis_depth = 2           # nuevo — default 1
min_relational_cohesion = 1.5  # nuevo
max_package_classes = 20     # nuevo
max_package_ca = 10          # nuevo
coverage_report_path = "coverage.json"  # nuevo
min_coverage = 80.0          # nuevo

[tool.architectanalyst.layer_roles]  # nueva subsección
"*/application/commands/*" = "leaf"
"*/domain/ports/*" = "stable"
```

## Criterios de cierre del incremento

- [ ] `layer_roles` funcional en config e InstabilityAnalyzer
- [ ] `analysis_depth` funcional en config y DistanceAnalyzer
- [ ] RelationalCohesionAnalyzer implementado con auto-discovery
- [ ] GodPackageAnalyzer implementado con auto-discovery
- [ ] CoverageAnalyzer implementado con auto-discovery
- [ ] Todos los campos nuevos en `ArchitectAnalystConfig`
- [ ] Toggles en `[tool.architectanalyst.checks]` para nuevas métricas (hereda de Incremento 1)
- [ ] Tests unitarios por métrica
- [ ] Snapshots históricos incluyen nuevas métricas
- [ ] `ruff` y `mypy` limpios
- [ ] `pytest` completo verde
