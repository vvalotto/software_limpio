# Incremento 3 — Nuevos analyzers DesignReviewer

**Versión:** v0.4.0
**Prioridad:** Media
**Requiere:** Incremento 1 completo
**Branch sugerido:** `mejora-incremento-3-designreviewer-analyzers`

## Objetivo

Extender DesignReviewer con nuevos analyzers que cubren smells de diseño OO no detectados actualmente, y resolver el spike de SOLID para definir si se agregan analyzers de principios.

## Issues incluidos

- [ ] #59 — Spike: evaluar implementación de analizador de Principios SOLID
- [ ] #54 — LawOfDemeterAnalyzer — cadenas de acceso que violan encapsulamiento
- [ ] #55 — PrimitiveObsessionAnalyzer — primitivos donde deberían ser Value Objects
- [ ] (pendiente spike #59) — ISP y/o DIP si el spike los valida

## Orden de implementación

1. **#59 Spike SOLID** — resolver primero para saber si se agregan analyzers de principios en este incremento o en el siguiente
2. **#54 LawOfDemeterAnalyzer** — AST puro, independiente
3. **#55 PrimitiveObsessionAnalyzer** — AST puro, independiente
4. **(si spike aprueba) ISP y/o DIP** — al final del incremento

## Patrón de implementación (igual para todos)

Para cada analyzer:
1. Crear `src/quality_agents/designreviewer/analyzers/<nombre>_analyzer.py` heredando de `Verifiable`
2. Agregar umbral en `DesignReviewerConfig` si aplica
3. Exportar en `analyzers/__init__.py`
4. Tests unitarios en `tests/unit/test_design_<nombre>_analyzer.py`

## Notas de diseño

**LawOfDemeterAnalyzer:**
- Recorrer el AST buscando cadenas de atributos (`a.b.c`) con profundidad > `max_demeter_depth`
- Excluir accesos sobre `self` — son legítimos
- Cuidado con fluent interfaces (builders, querysets): considerar lista de exclusiones configurable

**PrimitiveObsessionAnalyzer:**
- Buscar firmas de métodos con N+ parámetros anotados con el mismo tipo primitivo (`str`, `int`, `float`)
- Buscar parámetros `dict` / `Dict[str, Any]` en métodos públicos
- Excluir `__init__` de dataclasses y `@classmethod` constructores

## Criterios de cierre del incremento

- [ ] Spike #59 resuelto con decisión documentada
- [ ] LawOfDemeterAnalyzer implementado con auto-discovery
- [ ] PrimitiveObsessionAnalyzer implementado con auto-discovery
- [ ] Toggles en `[tool.designreviewer.checks]` para nuevos analyzers (hereda de Incremento 1)
- [ ] Tests unitarios por analyzer
- [ ] `ruff` y `mypy` limpios
- [ ] `pytest` completo verde
