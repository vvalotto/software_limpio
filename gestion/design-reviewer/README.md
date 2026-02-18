# Gestión — DesignReviewer (v0.2.0)

Carpeta de gestión del trabajo de implementación de DesignReviewer.

## Estructura

Cada subcarpeta corresponde a una fase del plan `gestion/releases/v0.2.0-plan.md`.
Los tickets se generan al iniciar cada fase como archivos `.md` individuales.

## Flujo de trabajo

- **Inicio de fase** → se generan los tickets de la fase
- **Fin de ticket** → commit
- **Fin de fase** → push + PR

## Fases

| Carpeta | Descripción |
|---------|-------------|
| `fase-1-infraestructura/` | Reemplazar skeleton, orchestrator, config |
| `fase-2-acoplamiento/` | CBOAnalyzer, FanOutAnalyzer, CircularImportsAnalyzer |
| `fase-3-cohesion-herencia/` | LCOMAnalyzer, WMCAnalyzer, DITAnalyzer, NOPAnalyzer |
| `fase-4-code-smells-solid/` | Catálogo de smells + SOLID |
| `fase-5-cli-output/` | CLI Rich, JSON, exit codes |
| `fase-6-ia/` | Claude API opt-in, prompts, mocks |
| `fase-7-tests-documentacion/` | Tests E2E, guía de usuario, CHANGELOG |
| `fase-8-release/` | Build, tag, GitHub Release |
