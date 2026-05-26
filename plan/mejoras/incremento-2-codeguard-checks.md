# Incremento 2 — Nuevos checks CodeGuard

**Versión:** v0.4.0
**Prioridad:** Media
**Requiere:** Incremento 1 completo
**Branch sugerido:** `mejora-incremento-2-codeguard-checks`

## Objetivo

Extender CodeGuard con tres nuevos checks modulares que cubren gaps en la calidad de código a nivel pre-commit.

## Issues incluidos

- [ ] #50 — MaintainabilityCheck (`radon mi`) — Maintainability Index por archivo
- [ ] #51 — DeadCodeCheck (`vulture`) — código muerto: funciones, clases y variables no usadas
- [ ] #52 — SpellingCheck (`codespell`) — typos en nombres, comentarios y strings

## Orden de implementación

Los tres checks son independientes entre sí. Orden sugerido por impacto:

1. **#51 DeadCodeCheck** — mayor valor diagnóstico, `vulture` no tiene superposición con checks existentes
2. **#50 MaintainabilityCheck** — complementa `ComplexityCheck` con visión de archivo completo
3. **#52 SpellingCheck** — menor prioridad, más opinable

## Patrón de implementación (igual para los tres)

Para cada check:
1. Crear `src/quality_agents/codeguard/checks/<nombre>_check.py` heredando de `Verifiable`
2. Agregar campo de config en `CodeGuardConfig` (umbral o parámetro relevante)
3. Exportar en `checks/__init__.py` (auto-discovery lo levanta solo)
4. Tests unitarios en `tests/unit/test_codeguard_<nombre>_check.py`

## Dependencias de herramientas

Agregar al `pyproject.toml` en `[project.optional-dependencies]` o `[project.dependencies]`:
- `vulture` — DeadCodeCheck
- `radon` — ya está (ComplexityCheck lo usa)
- `codespell` — SpellingCheck

## Criterios de cierre del incremento

- [ ] Tres checks implementados con auto-discovery
- [ ] Campos de config agregados en `CodeGuardConfig`
- [ ] Toggle en `[tool.codeguard.checks]` para cada nuevo check (hereda de Incremento 1)
- [ ] Tests unitarios por check
- [ ] `ruff` y `mypy` limpios
- [ ] `pytest` completo verde
