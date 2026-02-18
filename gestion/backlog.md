# Backlog — Software Limpio

Features y mejoras pendientes ordenadas por versión objetivo.

---

## v0.2.0 — DesignReviewer

Análisis de diseño para Pull Requests (~2-5 min).

- [ ] Implementar arquitectura modular (analyzers) siguiendo patrón Verifiable
- [ ] `CodeSmellAnalyzer` — detección de god objects, feature envy, data clumps
- [ ] `CouplingAnalyzer` — CBO (Coupling Between Objects) con radon/pydeps
- [ ] `CohesionAnalyzer` — LCOM (Lack of Cohesion of Methods)
- [ ] `DuplicationAnalyzer` — detección de código duplicado
- [ ] CLI `designreviewer` funcional
- [ ] Sugerencias de refactoring (con IA opcional)
- [ ] Tests (objetivo: ~150 tests nuevos)
- [ ] Documentación de usuario

---

## v0.3.0 — ArchitectAnalyst

Análisis de tendencias arquitectónicas al fin de sprint (~10-30 min).

- [ ] Implementar arquitectura modular (metrics) siguiendo patrón Verifiable
- [ ] `LayerViolationMetric` — detección de violaciones de capas
- [ ] `DependencyCycleMetric` — ciclos de dependencias con pydeps
- [ ] `MaintainabilityMetric` — índice de mantenibilidad histórico (radon)
- [ ] Persistencia histórica en SQLite
- [ ] Dashboards interactivos con Plotly
- [ ] CLI `architectanalyst` funcional
- [ ] Tests (objetivo: ~150 tests nuevos)
- [ ] Documentación de usuario

---

## v1.0.0 — Trilogía Completa

- [ ] API estable y documentada para los 3 agentes
- [ ] Publicación en PyPI (`pip install quality-agents`)
- [ ] GitHub Actions CI/CD completo
- [ ] Integración de los 3 agentes en un pipeline unificado

---

## Mejoras Transversales (sin versión asignada)

- [ ] GitHub Actions — pipeline de tests automático en cada push/PR
- [ ] Cache de resultados para análisis incremental
- [ ] Soporte para plugins personalizados (checks de usuario)
- [ ] Análisis paralelo de checks (ThreadPoolExecutor)
- [ ] Badge de cobertura en README
