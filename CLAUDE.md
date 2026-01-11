# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Software Limpio** is a Python framework implementing a three-tier automated quality control system, inspired by Robert C. Martin's trilogy (Clean Code, Clean Architecture) with the addition of "Clean Design".

- **Language:** Python 3.11+
- **Documentation language:** Spanish
- **Virtual environment:** `.venv`

## Development Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/unit/test_codeguard.py

# Run a specific test
pytest tests/unit/test_codeguard.py::TestCodeGuard::test_init_without_config

# Run tests with coverage
pytest --cov=src/quality_agents --cov-report=html

# Format code
black src/ tests/
isort src/ tests/

# Linting
ruff check src/ tests/
mypy src/
```

## CLI Entry Points

After installation, three CLI commands are available:

```bash
codeguard           # Pre-commit agent
designreviewer      # PR/Review agent
architectanalyst    # Sprint-end agent
```

## Architecture

Three-tier quality control system:

```
Pre-commit (<5s)        →    PR Review (2-5min)    →    Sprint End (10-30min)
      ↓                            ↓                           ↓
  CodeGuard                  DesignReviewer             ArchitectAnalyst
 (warns only)               (blocks if critical)        (trend analysis)
```

### Agent Structure

Each agent follows the same pattern in `src/quality_agents/<agent>/`:
- `agent.py` - Main class with `run()` method
- `checks.py` or `analyzers.py` - Individual verification/analysis functions
- `config.py` - Agent-specific configuration (loads from `configs/<agent>.yml`)

Shared utilities in `src/quality_agents/shared/`:
- `config.py` - `QualityConfig` dataclass, loads YAML with `load_config()`
- `reporting.py` - Report generation utilities

### Key Implementation Details

- Configuration loaded via `QualityConfig.from_yaml()` with fallback to defaults
- Each check returns `CheckResult` with `Severity` (INFO/WARNING/ERROR)
- Tests use `temp_project` and `sample_python_file` fixtures from `tests/conftest.py`

## Quality Thresholds

Defined in `QualityConfig` (`src/quality_agents/shared/config.py`):
- Cyclomatic Complexity: ≤ 10
- Function lines: ≤ 20
- CBO (Coupling): ≤ 5
- LCOM (Cohesion): ≤ 1
- Maintainability Index: > 20

## Key Reference Files

- `docs/agentes/especificacion_agentes_calidad.md` - Agent specifications
- `docs/metricas/Metricas_Clasificadas.md` - Metrics classification
- `SESION.md` - Session context and current tasks (read at session start)

## Session Management

Use the custom Claude Code commands:
- `/sesion` - Load session context at start
- `/guardar-sesion` - Save progress before ending
