# Backlog — Software Limpio

Features y mejoras pendientes ordenadas por versión objetivo.

---

## v0.2.0 — DesignReviewer ✅ (Febrero 2026)

Análisis de diseño para Pull Requests (~2-5 min).

- [x] Implementar arquitectura modular (analyzers) siguiendo patrón Verifiable
- [x] 12 analyzers: CBO, FanOut, CircularImports, LCOM, WMC, DIT, NOP, GodObject, LongMethod, LongParameterList, FeatureEnvy, DataClumps
- [x] CLI `designreviewer` funcional (Rich + JSON, exit code 1 si CRITICAL)
- [x] Tests (~160 tests nuevos)
- [x] Documentación de usuario

---

## v0.3.0 — ArchitectAnalyst ✅ (Marzo 2026)

Análisis de tendencias arquitectónicas al fin de sprint (~10-30 min).

- [x] Implementar arquitectura modular (metrics) siguiendo patrón Verifiable
- [x] 7 métricas: Ca, Ce, I, A, D (Martin) + DependencyCycles + LayerViolations
- [x] Persistencia histórica en SQLite (SnapshotStore)
- [x] Comparación de tendencias entre sprints (TrendCalculator: ↑↓=)
- [x] CLI `architectanalyst` funcional (Rich + JSON, exit code 0 — informativo)
- [x] Tests (~200 tests nuevos)
- [x] Documentación de usuario

---

## v0.4.0 — Integración IA opt-in (pendiente)

- [ ] CodeGuard: explicaciones IA para warnings (opt-in, `[tool.codeguard.ai] enabled = true`)
- [ ] DesignReviewer: sugerencias de refactorización IA (opt-in)
- [ ] ArchitectAnalyst: análisis estratégico IA con histórico de sprints (opt-in)
- [ ] Publicación en PyPI (`pip install quality-agents`)
- [ ] GitHub Actions CI/CD

---

## v1.0.0 — Trilogía Completa

- [ ] API estable y documentada para los 3 agentes
- [ ] Integración de los 3 agentes en un pipeline unificado
- [ ] Guías para uso académico / estudiantes

---

## Mejoras Transversales (sin versión asignada)

- [ ] GitHub Actions — pipeline de tests automático en cada push/PR
- [ ] Cache de resultados para análisis incremental
- [ ] Soporte para plugins personalizados (checks de usuario)
- [ ] Análisis paralelo de checks (ThreadPoolExecutor)
- [ ] Badge de cobertura en README
