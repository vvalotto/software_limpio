# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Software Limpio** is an educational and practical Python framework implementing a three-tier automated quality control system, inspired by Robert C. Martin's trilogy (Clean Code, Clean Architecture) with the addition of "Clean Design".

**Vision:** Transform developers from "code writers" to "quality evaluators" through AI agents that detect, explain, and suggest improvements in real-time.

- **Language:** Python 3.11+
- **Documentation language:** Spanish (Rioplatense)
- **Virtual environment:** `.venv`
- **Package name:** `quality-agents`

## Development Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/unit/test_codeguard_config.py

# Run a specific test
pytest tests/unit/test_codeguard_config.py::TestLoadConfig::test_load_config_from_pyproject_toml

# Run tests with coverage
pytest --cov=src/quality_agents --cov-report=html

# Format code (line-length=100)
black src/ tests/
isort src/ tests/

# Linting
ruff check src/ tests/
mypy src/
```

## CLI Entry Points

After installation (`pip install -e ".[dev]"`), three CLI commands are available:

```bash
# CodeGuard - Quick pre-commit quality checks (<5s, warns only)
codeguard .                              # Analyze current directory
codeguard src/                           # Analyze specific directory
codeguard --config configs/codeguard.yml # Use custom config
codeguard --format json .                # JSON output

# DesignReviewer - PR/Review analysis (2-5min, blocks if critical)
designreviewer                           # (implementation pending)

# ArchitectAnalyst - Sprint-end trend analysis (10-30min)
architectanalyst                         # (implementation pending)
```

## CodeGuard Configuration

CodeGuard uses `pyproject.toml` for configuration (PEP 518 standard):

```toml
[tool.codeguard]
# Quality thresholds
min_pylint_score = 8.0
max_cyclomatic_complexity = 10
max_line_length = 100
max_function_lines = 20

# Enabled checks
check_pep8 = true
check_pylint = true
check_security = true
check_complexity = true
check_types = true
check_imports = true

# Exclusions
exclude_patterns = ["*.pyc", "__pycache__", ".venv", "migrations"]

# AI configuration (opt-in)
[tool.codeguard.ai]
enabled = false              # Set to true to enable AI explanations
explain_errors = true        # AI explains detected errors
suggest_fixes = true         # AI suggests fixes
max_tokens = 500            # Max tokens for AI responses
```

Fallback to `.codeguard.yml` is supported for backward compatibility.

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
- `agent.py` - Main class with `run()` method that returns results
- `checks.py` or `analyzers.py` - Individual verification/analysis functions
- `config.py` - Agent-specific configuration
  - **CodeGuard:** `CodeGuardConfig` + `AIConfig` dataclasses with `from_pyproject_toml()`, `from_yaml()`, and `load_config()`
  - **Other agents:** Load from YAML in `configs/<agent>.yml`
- `PLAN_IMPLEMENTACION.md` - Implementation roadmap (CodeGuard only, for now)

Shared utilities in `src/quality_agents/shared/`:
- `config.py` - `QualityConfig` dataclass with `from_yaml()` class method
- `reporting.py` - Report generation utilities

### Configuration Loading

**CodeGuard** uses modern pyproject.toml configuration (PEP 518) with YAML fallback:
- Primary: `pyproject.toml` → `[tool.codeguard]` section
- Fallback: `.codeguard.yml` for backward compatibility
- Auto-discovery via `load_config(config_path, project_root)` function
- Search order: explicit path → pyproject.toml → .codeguard.yml → defaults
- AI configuration in `[tool.codeguard.ai]` subsection (opt-in)

**Other agents** use YAML configuration in `configs/<agent>.yml`:
- Load via `QualityConfig.from_yaml(path)` with automatic fallback to defaults
- Standard search paths: `.quality.yml`, `.quality.yaml`, `configs/quality.yml`

### Return Types

- Each check returns `CheckResult` with:
  - `check_name: str`
  - `severity: Severity` (INFO/WARNING/ERROR enum)
  - `message: str`
  - `file_path: Optional[str]`
  - `line_number: Optional[int]`

### Test Fixtures

Available in `tests/conftest.py`:
- `temp_project` - Creates temporary project structure with `src/sample.py`
- `sample_python_file` - Returns path to sample Python file
- `empty_config` - Returns default `QualityConfig` instance

## Fundamental Principles

The framework is built on 6 fundamental principles, all documented in `docs/teoria/fundamentos/`:
1. **Modularidad** (Parnas 1972)
2. **Ocultamiento de información** (Parnas 1972)
3. **Cohesión** (Constantine 1968)
4. **Acoplamiento** (Constantine 1968)
5. **Separación de concerns** (Dijkstra 1974)
6. **Abstracción** (Liskov 1974)

Each principle is applied at three levels: Código, Diseño, and Arquitectura.

## Quality Thresholds

Defined in `QualityConfig.thresholds` (`src/quality_agents/shared/config.py`):

**Code Level:**
- Cyclomatic Complexity: ≤ 10
- Function lines: ≤ 20
- Nesting depth: ≤ 4
- Line length: ≤ 100 (also in Black config)

**Design Level:**
- CBO (Coupling): ≤ 5
- LCOM (Cohesion): ≤ 1
- Maintainability Index: > 20
- WMC (Weighted Methods): ≤ 20

**Architecture Level:**
- Distance from main sequence: ≤ 0.3
- Layer violations: 0
- Dependency cycles: 0

## Documentation Style

When writing docs in `docs/teoria/`:
- Follow `docs/teoria/GUIA_REDACCION.md` style guide
- Spanish (Rioplatense), concise, direct
- Structure: Definición → Por qué importa → Cómo se aplica → Métricas
- Show principle application at 3 levels: Código, Diseño, Arquitectura

## Key Reference Files

- `SESION.md` - **Read first** - Current tasks, decisions, and session context
- `docs/agentes/especificacion_agentes_calidad.md` - Complete agent specifications (v1.1)
- `docs/agentes/guia_implementacion_agentes.md` - Implementation guide
- `docs/agentes/ajuste_documentacion.md` - 5 architectural decisions (January 2026)
- `src/quality_agents/codeguard/PLAN_IMPLEMENTACION.md` - CodeGuard implementation plan (7 phases, 27 tickets)
- `docs/metricas/Metricas_Clasificadas.md` - Metrics classification
- `docs/teoria/GUIA_REDACCION.md` - Writing style guide for theory docs
- `docs/guias/codeguard.md` - User guide for CodeGuard
- `plan/plan_proyecto.md` - Detailed project plan

## Technical Decisions

- **AI Integration:** Claude API (model: `claude-sonnet-4-20250514`)
- **Database:** SQLite for ArchitectAnalyst historical metrics
- **Dashboards:** Plotly (not Dash, not Streamlit)
- **CLI Framework:** Click for command-line interface
- **Console Output:** Rich for colored, formatted console output
- **Reports:** Jinja2 for HTML templates
- **Configuration:**
  - CodeGuard: `pyproject.toml` → `[tool.codeguard]` (PEP 518 standard) with YAML fallback
  - Other agents: YAML in `configs/<agent>.yml`

## Project Phase and Implementation Status

**Current Phase**: Phase 1 - CodeGuard as usable framework (45% complete)
**Active Branch**: `refactoring-fase-1-codeguard`

### Completed
- **Phase 0:** Theoretical documentation (`docs/teoria/` - all 4 sections complete)
  - 6 fundamental principles documented
  - Philosophical framework, Clean Trilogy, New Paradigm
- **CodeGuard Fase 1:** Modern configuration system ✅
  - pyproject.toml support with `[tool.codeguard]` (PEP 518)
  - AI configuration via `[tool.codeguard.ai]` subsection (opt-in)
  - Auto-discovery function `load_config()` with priority search
  - 19 unit tests passing (100% coverage for config)
- CLI infrastructure with Click (entry point works)
- File collection mechanism (`collect_files()` working)
- Project structure and test fixtures
- User guides (`docs/guias/codeguard.md`)

### In Progress (Phase 1 - Fase 2)
- Individual quality checks implementation (flake8, pylint, bandit, radon, mypy, imports)
- Integration of checks in `CodeGuard.run()` method
- Rich console output formatting

### Pending Branches
- `fase-0-fundamentos` - Ready for PR to main
- `refactoring-fase-1-codeguard` - In progress (Fase 1 complete, moving to Fase 2)

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

### Dependencies

**TOML parsing** (for pyproject.toml):
- Python 3.11+: Uses built-in `tomllib`
- Python < 3.11: Uses `tomli` package (installed via `pyproject.toml` conditional dependency)

## Session Management

Custom Claude Code commands (restart Claude Code after changes):
- `/sesion` - Load session context at start
- `/guardar-sesion` - Save progress before ending
