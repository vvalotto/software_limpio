# Backlog — Software Limpio

Features y mejoras pendientes ordenadas por versión objetivo.

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

- [ ] `examples/sample_project`: expandir para demostrar DesignReviewer y ArchitectAnalyst
  - Agregar código con problemas de acoplamiento (CBO, FanOut, CircularImports)
  - Agregar estructura de paquetes con imports entre sí para métricas de Martin
  - Actualizar `demo.sh` para incluir los tres agentes
- [ ] Cache de resultados para análisis incremental
- [ ] Soporte para plugins personalizados (checks de usuario)
- [ ] Análisis paralelo de checks (ThreadPoolExecutor)
- [ ] Badge de cobertura en README
