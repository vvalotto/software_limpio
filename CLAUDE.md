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
# CodeGuard - Quick pre-commit quality checks
codeguard .                              # Analyze current directory
codeguard src/                           # Analyze specific directory
codeguard --config configs/codeguard.yml # Use custom config
codeguard --format json .                # JSON output

# DesignReviewer - PR/Review analysis
designreviewer                           # (implementation pending)

# ArchitectAnalyst - Sprint-end trend analysis
architectanalyst                         # (implementation pending)
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
- `docs/teoria/GUIA_REDACCION.md` - Writing style guide for theory docs
- `SESION.md` - Session context and current tasks (read at session start)

## Project Phase and Implementation Status

**Current Phase**: Phase 1 - CodeGuard as usable framework
**Active Branch**: `fase-1-codeguard`

### Completed
- CLI infrastructure with Click (entry point works)
- File collection mechanism (`collect_files()` working)
- Project structure and test fixtures

### In Progress
- YAML configuration loading
- Individual quality checks (flake8, pylint, bandit, radon)
- Rich console output formatting

### Implementation Pattern

When implementing checks in agents, follow this pattern:
1. Import check results as `CheckResult` with `Severity` enum
2. Return structured results from individual check methods
3. Aggregate all results in the `run()` method
4. Use configuration thresholds from `QualityConfig`

### Tool Configuration

All quality tools have standardized configurations in `pyproject.toml`:
- Black: line-length 100, Python 3.11+
- isort: black-compatible profile
- Ruff: E, F, W, I, N, B, C4 rules (ignoring E501)
- mypy: strict mode with typed defs required
- pytest: verbose with short tracebacks

## Session Management

Use the custom Claude Code commands:
- `/sesion` - Load session context at start
- `/guardar-sesion` - Save progress before ending
