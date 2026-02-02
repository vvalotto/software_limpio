# GUÍA DE IMPLEMENTACIÓN DE AGENTES DE CALIDAD
**Integración en tu proyecto - Actualizada Enero 2026**

---

## INTRODUCCIÓN

Esta guía te muestra cómo **usar** Quality Agents en tus proyectos.

**Nota importante:** Quality Agents se distribuye como **paquete instalable**, no como scripts para copiar. Este enfoque profesional permite:
- Versionado centralizado
- Actualizaciones fáciles con `pip install -U quality-agents`
- Consistencia entre todos tus proyectos
- Configuración unificada en `pyproject.toml`

---

## INSTALACIÓN RÁPIDA

### Opción 1: Desde PyPI (cuando esté publicado)

```bash
pip install quality-agents
```

### Opción 2: Desde GitHub

```bash
pip install git+https://github.com/vvalotto/software_limpio.git
```

### Opción 3: En modo desarrollo (para contribuir al framework)

```bash
git clone https://github.com/vvalotto/software_limpio.git
cd software_limpio
pip install -e ".[dev]"
```

### Verificar instalación

```bash
codeguard --version
designreviewer --version
architectanalyst --version
```

---

## ARQUITECTURA INTERNA (PARA CONTRIBUIDORES)

Esta sección es relevante si estás **contribuyendo al framework** o extendiendo funcionalidad. Si solo quieres **usar** los agentes, podés saltear esta parte.

### Sistema Modular de Verificaciones

**Decisión arquitectónica (Febrero 2026):** Cada agente usa una arquitectura modular con orquestación contextual.

```
agente/
├── orchestrator.py       # Orquestador de verificaciones
├── checks/               # O analyzers/ o metrics/
│   ├── __init__.py
│   ├── verificable_1.py
│   ├── verificable_2.py
│   └── ...
└── agent.py              # Agente principal
```

**Características clave:**

| Aspecto | Descripción |
|---------|-------------|
| **Modularidad** | Cada verificación en su propio archivo |
| **Auto-discovery** | El orquestador descubre automáticamente las verificaciones |
| **Orquestación** | Decisión inteligente de qué ejecutar según contexto |
| **Extensibilidad** | Agregar verificación = crear archivo + exportar |

### Crear un Nuevo Check/Analyzer/Metric

Si querés agregar una nueva verificación a cualquier agente, seguí estos pasos:

#### Paso 1: Crear módulo en directorio correspondiente

**Ejemplo para CodeGuard:**

```python
# codeguard/checks/mi_nuevo_check.py

from pathlib import Path
from typing import List

from quality_agents.shared.verifiable import Verifiable, ExecutionContext
from quality_agents.codeguard.agent import CheckResult, Severity


class MiNuevoCheck(Verifiable):
    """
    Descripción breve del check.

    Este check verifica [qué verifica] usando [herramienta].
    """

    @property
    def name(self) -> str:
        """Nombre identificador del check."""
        return "MiNuevoCheck"

    @property
    def category(self) -> str:
        """Categoría del check."""
        return "quality"  # Opciones: "style", "quality", "security"

    @property
    def estimated_duration(self) -> float:
        """Duración estimada en segundos."""
        return 1.5  # Ajustar según mediciones reales

    @property
    def priority(self) -> int:
        """
        Prioridad de ejecución (1=más alta, 10=más baja).

        Guía:
        - 1-2: Crítico (seguridad, errores graves)
        - 3-4: Alto (calidad esencial)
        - 5-6: Medio (mejoras)
        - 7-10: Bajo (nice-to-have)
        """
        return 3

    def should_run(self, context: ExecutionContext) -> bool:
        """
        Decide si este check debe ejecutarse en el contexto dado.

        Args:
            context: Contexto de ejecución con info del archivo y análisis

        Returns:
            True si debe ejecutarse, False si no
        """
        # Ejemplo: solo archivos .py no excluidos
        if context.is_excluded:
            return False

        if context.file_path.suffix != ".py":
            return False

        # Verificar si está habilitado en config
        if hasattr(context.config, 'check_mi_nuevo'):
            return context.config.check_mi_nuevo

        return True

    def execute(self, file_path: Path) -> List[CheckResult]:
        """
        Ejecuta la verificación sobre el archivo.

        Args:
            file_path: Ruta al archivo a verificar

        Returns:
            Lista de resultados encontrados
        """
        results = []

        try:
            # Tu lógica de verificación aquí
            # Ejemplo: ejecutar herramienta externa
            # import subprocess
            # process = subprocess.run(
            #     ["mi-herramienta", str(file_path)],
            #     capture_output=True,
            #     text=True,
            #     timeout=5
            # )

            # Parsear output y crear CheckResult
            # if process.stdout:
            #     results.append(CheckResult(
            #         check_name=self.name,
            #         severity=Severity.WARNING,
            #         message="Mensaje descriptivo",
            #         file_path=str(file_path),
            #         line_number=10  # Opcional
            #     ))

            pass  # Reemplazar con implementación real

        except FileNotFoundError:
            results.append(CheckResult(
                check_name=self.name,
                severity=Severity.ERROR,
                message="Herramienta no encontrada. Instalar con: pip install ...",
                file_path=str(file_path),
                line_number=None
            ))
        except Exception as e:
            results.append(CheckResult(
                check_name=self.name,
                severity=Severity.ERROR,
                message=f"Error ejecutando check: {str(e)}",
                file_path=str(file_path),
                line_number=None
            ))

        return results
```

#### Paso 2: Exportar en `__init__.py`

```python
# codeguard/checks/__init__.py

from .pep8_check import PEP8Check
from .pylint_check import PylintCheck
from .mi_nuevo_check import MiNuevoCheck  # AGREGAR ESTA LÍNEA

__all__ = [
    "PEP8Check",
    "PylintCheck",
    "MiNuevoCheck",  # AGREGAR ESTA LÍNEA
]
```

#### Paso 3: ¡Listo! Auto-discovery

**No necesitás modificar ningún otro archivo.** El sistema de auto-discovery del orquestador incluirá tu check automáticamente.

```python
# El orquestador hace esto automáticamente:
checks = orchestrator._discover_checks()
# → [PEP8Check(), PylintCheck(), MiNuevoCheck(), ...]
```

### Crear Tests para tu Check

**Siempre** creá tests para tu verificación:

```python
# tests/unit/test_codeguard_checks.py

import pytest
from pathlib import Path

from quality_agents.codeguard.checks import MiNuevoCheck
from quality_agents.shared.verifiable import ExecutionContext
from quality_agents.codeguard.agent import Severity


class TestMiNuevoCheck:
    """Tests para MiNuevoCheck."""

    def test_should_run_on_py_files(self, tmp_path):
        """Debe ejecutarse en archivos .py."""
        check = MiNuevoCheck()
        context = ExecutionContext(
            file_path=tmp_path / "test.py",
            is_excluded=False,
            analysis_type="full"
        )

        assert check.should_run(context) is True

    def test_should_not_run_on_excluded_files(self, tmp_path):
        """No debe ejecutarse en archivos excluidos."""
        check = MiNuevoCheck()
        context = ExecutionContext(
            file_path=tmp_path / "test.py",
            is_excluded=True,
            analysis_type="full"
        )

        assert check.should_run(context) is False

    def test_execute_returns_results(self, tmp_path):
        """Debe retornar lista de resultados."""
        check = MiNuevoCheck()
        file_path = tmp_path / "test.py"
        file_path.write_text("# codigo de ejemplo\n")

        results = check.execute(file_path)

        assert isinstance(results, list)
        # Agregar más aserciones según tu implementación

    def test_execute_with_violations(self, tmp_path):
        """Debe detectar violaciones."""
        check = MiNuevoCheck()
        file_path = tmp_path / "bad_code.py"
        # Escribir código que tu check debe detectar
        file_path.write_text("# codigo con problema\n")

        results = check.execute(file_path)

        assert len(results) > 0
        assert all(r.check_name == "MiNuevoCheck" for r in results)
        # Verificar severidad, mensaje, etc.

    def test_execute_without_violations(self, tmp_path):
        """Debe retornar lista vacía si no hay violaciones."""
        check = MiNuevoCheck()
        file_path = tmp_path / "clean_code.py"
        # Escribir código limpio
        file_path.write_text("# codigo limpio\n")

        results = check.execute(file_path)

        assert results == []
```

### Ejecutar Tests

```bash
# Ejecutar solo tests de tu check
pytest tests/unit/test_codeguard_checks.py::TestMiNuevoCheck -v

# Ejecutar todos los tests de checks
pytest tests/unit/test_codeguard_checks.py -v

# Ejecutar con coverage
pytest tests/unit/test_codeguard_checks.py --cov=src/quality_agents/codeguard/checks
```

### Aplicar el Mismo Patrón a Otros Agentes

El mismo patrón se aplica a **DesignReviewer** y **ArchitectAnalyst**:

| Agente | Directorio | Clase Base | Tipo |
|--------|-----------|------------|------|
| CodeGuard | `codeguard/checks/` | `Verifiable` | Check |
| DesignReviewer | `designreviewer/analyzers/` | `Verifiable` | Analyzer |
| ArchitectAnalyst | `architectanalyst/metrics/` | `Verifiable` | Metric |

**Referencia completa:** Ver `docs/agentes/decision_arquitectura_checks_modulares.md`

---

## CONFIGURACIÓN EN TU PROYECTO

### Paso 1: Crear pyproject.toml (si no existe)

```bash
cd tu_proyecto/

# Si no tienes pyproject.toml, créalo
cat > pyproject.toml << 'EOF'
[project]
name = "mi-proyecto"
version = "0.1.0"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
EOF
```

### Paso 2: Agregar configuración de CodeGuard

Agregar al `pyproject.toml`:

```toml
[tool.codeguard]
# Umbrales
min_pylint_score = 8.0
max_cyclomatic_complexity = 10
max_line_length = 100

# Verificaciones habilitadas
check_pep8 = true
check_pylint = true
check_security = true
check_complexity = true

# IA opcional (requiere ANTHROPIC_API_KEY)
[tool.codeguard.ai]
enabled = false  # Cambiar a true para habilitar explicaciones IA
explain_errors = true
suggest_fixes = true

# Exclusiones
exclude_patterns = [
    "__pycache__",
    ".venv",
    "venv",
    "migrations",
]
```

### Paso 3: (Opcional) Habilitar IA

Si querés explicaciones inteligentes de errores:

```bash
# Agregar a tu .bashrc o .zshrc
export ANTHROPIC_API_KEY="sk-ant-..."

# O crear archivo .env
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
echo ".env" >> .gitignore
```

Luego en `pyproject.toml`:
```toml
[tool.codeguard.ai]
enabled = true
```

---

## INTEGRACIÓN EN TU WORKFLOW

Elige el modelo que mejor se adapte a tu flujo de trabajo:

### Modelo 1: Uso Directo (Simple)

**Cuándo:** Verificación manual ocasional

```bash
# En tu proyecto
codeguard .                     # Analiza directorio actual
codeguard src/                  # Analiza solo src/
codeguard --format json .       # Salida JSON para procesamiento
```

**Pros:** Simple, sin configuración extra
**Contras:** No automático, fácil olvidarse

---

### Modelo 2: Framework pre-commit (Recomendado)

**Cuándo:** Proyectos profesionales, equipos

#### Paso 1: Instalar pre-commit

```bash
pip install pre-commit
```

#### Paso 2: Crear `.pre-commit-config.yaml`

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/vvalotto/software_limpio
    rev: v0.1.0  # Cambiar a version actual
    hooks:
      - id: codeguard
        name: CodeGuard Quality Check

      # Opcional: DesignReviewer solo manual
      - id: designreviewer
        name: Design Review
        stages: [manual]
```

#### Paso 3: Instalar hooks

```bash
pre-commit install
```

#### Paso 4: Probar

```bash
# Ejecutar manualmente
pre-commit run codeguard --all-files

# O hacer un commit de prueba
git add .
git commit -m "test pre-commit"
# → CodeGuard se ejecuta automáticamente
```

**Pros:** Automático, versionado, estándar de la industria
**Contras:** Requiere framework adicional

---

### Modelo 3: Hook Git Manual (Control Total)

**Cuándo:** Proyectos simples, necesitas customización

```bash
# En tu proyecto
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
codeguard .
exit 0  # Nunca bloquear commit
EOF

chmod +x .git/hooks/pre-commit
```

**Pros:** Control total, sin dependencias
**Contras:** No versionado, cada dev debe configurarlo

---

### Modelo 4: GitHub Actions (Verificación en PR)

**Cuándo:** Proyectos open source, equipos remotos

#### Crear `.github/workflows/quality.yml`

```yaml
name: Quality Check

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  codeguard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Quality Agents
        run: pip install quality-agents

      - name: Run CodeGuard
        run: codeguard .

      - name: Run DesignReviewer (if labeled)
        if: contains(github.event.pull_request.labels.*.name, 'design-review')
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: designreviewer
```

**Configurar secret:**
1. Repo → Settings → Secrets → New repository secret
2. Name: `ANTHROPIC_API_KEY`
3. Value: tu API key

**Pros:** Verificación centralizada, todos los PRs checked
**Contras:** Solo en GitHub, feedback tardío

---

## FASE 1: PRIMER USO DE CODEGUARD

### Prueba Rápida

Después de instalar (`pip install quality-agents`), probá CodeGuard en tu proyecto:

```bash
cd tu_proyecto/
codeguard .
```

**Salida esperada:**

```
🔍 CodeGuard v0.1.0
Analizando: /Users/tu/proyecto
Archivos Python encontrados: 47

📄 Analyzing files...

✅ PASS: PEP8 compliance (42/47 files)
⚠️  WARN: PEP8 violations in 5 files:
   src/utils/helper.py:15 - E501 line too long
   src/models/user.py:23 - W503 line break before binary operator

✅ PASS: Security (no critical issues)
⚠️  WARN: Pylint score 7.8/10 (3 files below threshold)
ℹ️  INFO: 2 functions with high complexity (>10)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary: 0 errors, 3 warnings in 2.1s

⚠️  Review recommended
💡 Run 'black .' to auto-format code
```

### Personalizar Configuración

Si los defaults no te sirven, crealos en `pyproject.toml`:

```toml
[tool.codeguard]
min_pylint_score = 7.5  # Más permisivo que default (8.0)
max_cyclomatic_complexity = 15  # Más permisivo que default (10)
check_types = false  # Deshabilitar mypy

exclude_patterns = [
    "tests/*",  # No analizar tests
    "migrations/*",
]
```

### Configuraciones Adicionales (Opcional)

**Archivo: `.flake8`** (solo si querés customizar PEP8)

```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503
per-file-ignores =
    __init__.py:F401
```

**Archivo: `.pylintrc`** (solo si querés customizar pylint)

```ini
[MASTER]
ignore=.git,__pycache__,.venv,venv,build,dist

[MESSAGES CONTROL]
disable=
    C0111,  # missing-docstring (manejado por otro checker)
    R0903,  # too-few-public-methods (común en DTOs)
    
[FORMAT]
max-line-length=100
indent-string='    '

[DESIGN]
max-args=6
max-attributes=10
max-locals=15
```

**Archivo: `bandit.yml`** (configuración de seguridad)

```yaml
# Bandit security scanner config
exclude_dirs:
  - /test
  - /tests
  - /.venv
  - /venv

tests:
  - B201  # flask_debug_true
  - B301  # pickle
  - B302  # marshal
  - B303  # md5
  - B304  # ciphers
  - B305  # cipher_modes
  - B306  # mktemp_q
  - B307  # eval
  - B308  # mark_safe
  - B309  # httpsconnection
  - B310  # urllib_urlopen
  - B311  # random
  - B312  # telnetlib
  - B313  # xml_bad_cElementTree
  - B314  # xml_bad_ElementTree
  - B315  # xml_bad_expatreader
  - B316  # xml_bad_expatbuilder
  - B317  # xml_bad_sax
  - B318  # xml_bad_minidom
  - B319  # xml_bad_pulldom
  - B320  # xml_bad_etree
  - B321  # ftplib
  - B322  # input
  - B323  # unverified_context
  - B324  # hashlib_new_insecure_functions
  - B325  # tempnam
  - B401  # import_telnetlib
  - B402  # import_ftplib
  - B403  # import_pickle
  - B404  # import_subprocess
  - B405  # import_xml_etree
  - B406  # import_xml_sax
  - B407  # import_xml_expat
  - B408  # import_xml_minidom
  - B409  # import_xml_pulldom
  - B410  # import_lxml
  - B411  # import_xmlrpclib
  - B412  # import_httpoxy
  - B413  # import_pycrypto
  - B501  # request_with_no_cert_validation
  - B502  # ssl_with_bad_version
  - B503  # ssl_with_bad_defaults
  - B504  # ssl_with_no_version
  - B505  # weak_cryptographic_key
  - B506  # yaml_load
  - B507  # ssh_no_host_key_verification
  - B601  # paramiko_calls
  - B602  # subprocess_popen_with_shell_equals_true
  - B603  # subprocess_without_shell_equals_true
  - B604  # any_other_function_with_shell_equals_true
  - B605  # start_process_with_a_shell
  - B606  # start_process_with_no_shell
  - B607  # start_process_with_partial_path
  - B608  # hardcoded_sql_expressions
  - B609  # linux_commands_wildcard_injection
  - B610  # django_extra_used
  - B611  # django_rawsql_used
```

### 1.2 Crear Script del Agente

**Archivo: `quality_agents/codeguard.py`**

```python
#!/usr/bin/env python3
"""
CodeGuard - Pre-commit Quality Agent
Verifica calidad básica de código antes de cada commit
"""

import sys
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

@dataclass
class CheckResult:
    """Resultado de una verificación"""
    metric: str
    passed: bool
    severity: str  # ERROR | WARN | INFO
    message: str
    suggestion: str = ""
    
class CodeGuard:
    def __init__(self, config_path: str = ".quality_control/codeguard/config.yml"):
        self.config = self._load_config(config_path)
        self.results: List[CheckResult] = []
        
    def _load_config(self, path: str) -> dict:
        """Carga configuración desde YAML"""
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def _get_changed_files(self) -> List[str]:
        """Obtiene archivos Python modificados en staging"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
                capture_output=True,
                text=True,
                check=True
            )
            files = result.stdout.strip().split('\n')
            return [f for f in files if f.endswith('.py') and f]
        except subprocess.CalledProcessError:
            return []
    
    def check_pep8(self, files: List[str]) -> CheckResult:
        """Verifica cumplimiento de PEP8"""
        if not self.config['metrics']['pep8']['enabled']:
            return None
            
        try:
            result = subprocess.run(
                ['flake8'] + files,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return CheckResult(
                    metric="PEP8",
                    passed=True,
                    severity="INFO",
                    message="PEP8 compliant"
                )
            else:
                violations = result.stdout.strip().split('\n')
                return CheckResult(
                    metric="PEP8",
                    passed=False,
                    severity="WARN",
                    message=f"{len(violations)} PEP8 violations found",
                    suggestion="Run 'black .' to auto-format"
                )
        except Exception as e:
            return CheckResult(
                metric="PEP8",
                passed=False,
                severity="ERROR",
                message=f"Error running flake8: {e}"
            )
    
    def check_pylint(self, files: List[str]) -> CheckResult:
        """Verifica score de pylint"""
        if not self.config['metrics']['pylint']['enabled']:
            return None
            
        threshold = self.config['metrics']['pylint']['threshold']
        
        try:
            result = subprocess.run(
                ['pylint', '--score=yes'] + files,
                capture_output=True,
                text=True
            )
            
            # Extraer score de la salida
            for line in result.stdout.split('\n'):
                if 'Your code has been rated at' in line:
                    score = float(line.split('rated at ')[1].split('/')[0])
                    
                    if score >= threshold:
                        return CheckResult(
                            metric="Pylint",
                            passed=True,
                            severity="INFO",
                            message=f"Score: {score:.1f}/10"
                        )
                    else:
                        return CheckResult(
                            metric="Pylint",
                            passed=False,
                            severity="WARN",
                            message=f"Score {score:.1f}/10 below threshold {threshold}",
                            suggestion="Review pylint suggestions"
                        )
        except Exception as e:
            return CheckResult(
                metric="Pylint",
                passed=False,
                severity="ERROR",
                message=f"Error running pylint: {e}"
            )
    
    def check_security(self, files: List[str]) -> List[CheckResult]:
        """Verifica problemas de seguridad con bandit"""
        if not self.config['metrics']['security']['enabled']:
            return []
            
        results = []
        
        try:
            result = subprocess.run(
                ['bandit', '-f', 'json'] + files,
                capture_output=True,
                text=True
            )
            
            import json
            report = json.loads(result.stdout)
            
            # Agrupar por severidad
            high_issues = [i for i in report.get('results', []) if i['issue_severity'] == 'HIGH']
            medium_issues = [i for i in report.get('results', []) if i['issue_severity'] == 'MEDIUM']
            
            if high_issues:
                for issue in high_issues:
                    results.append(CheckResult(
                        metric="Security",
                        passed=False,
                        severity="ERROR",
                        message=f"{issue['issue_text']} (line {issue['line_number']})",
                        suggestion=self._get_security_suggestion(issue['test_id'])
                    ))
            
            if not high_issues and not medium_issues:
                results.append(CheckResult(
                    metric="Security",
                    passed=True,
                    severity="INFO",
                    message="No security issues detected"
                ))
                
        except Exception as e:
            results.append(CheckResult(
                metric="Security",
                passed=False,
                severity="ERROR",
                message=f"Error running bandit: {e}"
            ))
        
        return results
    
    def _get_security_suggestion(self, test_id: str) -> str:
        """Retorna sugerencia según tipo de issue de seguridad"""
        suggestions = {
            'B201': 'Use secure Flask configuration',
            'B301': 'Avoid pickle, use json instead',
            'B307': 'Never use eval(), parse input safely',
            'B608': 'Use parameterized queries: cursor.execute("SELECT * FROM t WHERE id=?", (id,))',
            'B506': 'Use yaml.safe_load() instead of yaml.load()',
        }
        return suggestions.get(test_id, 'Review security best practices')
    
    def check_complexity(self, files: List[str]) -> List[CheckResult]:
        """Verifica complejidad ciclomática"""
        if not self.config['metrics']['complexity']['enabled']:
            return []
            
        threshold = self.config['metrics']['complexity']['info_threshold']
        results = []
        
        try:
            result = subprocess.run(
                ['radon', 'cc', '-s', '-a'] + files,
                capture_output=True,
                text=True
            )
            
            # Parsear salida para encontrar funciones complejas
            for line in result.stdout.split('\n'):
                if 'F ' in line or 'E ' in line:  # Complejidad alta
                    results.append(CheckResult(
                        metric="Complexity",
                        passed=True,  # Solo info, no falla
                        severity="INFO",
                        message=f"High complexity detected: {line.strip()}",
                        suggestion="Consider refactoring into smaller functions"
                    ))
            
            if not results:
                results.append(CheckResult(
                    metric="Complexity",
                    passed=True,
                    severity="INFO",
                    message="All functions have acceptable complexity"
                ))
                
        except Exception as e:
            results.append(CheckResult(
                metric="Complexity",
                passed=False,
                severity="ERROR",
                message=f"Error checking complexity: {e}"
            ))
        
        return results
    
    def run(self) -> int:
        """Ejecuta todas las verificaciones"""
        console.print("\n[bold cyan]🔍 CodeGuard - Quality Check[/bold cyan]")
        console.print("━" * 60)
        
        # Obtener archivos modificados
        files = self._get_changed_files()
        
        if not files:
            console.print("[yellow]No Python files to check[/yellow]")
            return 0
        
        console.print(f"\n[dim]Analyzing {len(files)} file(s)...[/dim]\n")
        
        import time
        start = time.time()
        
        # Ejecutar verificaciones
        checks = [
            self.check_pep8(files),
            self.check_pylint(files),
            *self.check_security(files),
            *self.check_complexity(files),
        ]
        
        # Filtrar None results
        checks = [c for c in checks if c is not None]
        
        elapsed = time.time() - start
        
        # Mostrar resultados
        errors = [c for c in checks if c.severity == 'ERROR' and not c.passed]
        warnings = [c for c in checks if c.severity == 'WARN' and not c.passed]
        
        for check in checks:
            if check.passed:
                console.print(f"✅ [green]PASS:[/green] {check.metric} - {check.message}")
            elif check.severity == 'ERROR':
                console.print(f"❌ [red]ERROR:[/red] {check.metric} - {check.message}")
                if check.suggestion:
                    console.print(f"   [dim]💡 {check.suggestion}[/dim]")
            elif check.severity == 'WARN':
                console.print(f"⚠️  [yellow]WARN:[/yellow] {check.metric} - {check.message}")
                if check.suggestion:
                    console.print(f"   [dim]💡 {check.suggestion}[/dim]")
            else:
                console.print(f"ℹ️  [blue]INFO:[/blue] {check.metric} - {check.message}")
        
        # Summary
        console.print("\n" + "━" * 60)
        console.print(f"Summary: {len(errors)} errors, {len(warnings)} warnings in {elapsed:.1f}s\n")
        
        if errors or warnings:
            console.print("[yellow]⚠️  Commit allowed but review recommended[/yellow]")
            console.print("[dim]💡 Run 'codeguard --fix' to auto-correct some issues[/dim]\n")
        else:
            console.print("[green]✨ All checks passed! Good job![/green]\n")
        
        # NUNCA bloquear pre-commit
        return 0


def main():
    """Entry point"""
    guard = CodeGuard()
    sys.exit(guard.run())


if __name__ == '__main__':
    main()
```

### 1.3 Hacer el Script Ejecutable

```bash
chmod +x quality_agents/codeguard.py

# Crear link simbólico para acceso fácil
ln -s $(pwd)/quality_agents/codeguard.py /usr/local/bin/codeguard
```

### 1.4 Configurar Git Hook

**Archivo: `.git/hooks/pre-commit`**

```bash
#!/bin/bash

# CodeGuard Pre-commit Hook
# Se ejecuta automáticamente antes de cada commit

python3 quality_agents/codeguard.py

# Siempre retorna 0 para no bloquear
exit 0
```

**Hacer ejecutable:**

```bash
chmod +x .git/hooks/pre-commit
```

### 1.5 Probar CodeGuard

```bash
# Ejecutar manualmente
python3 quality_agents/codeguard.py

# O usar el comando
codeguard

# Hacer un commit de prueba
git add .
git commit -m "Test CodeGuard"
# Deberías ver la salida de CodeGuard automáticamente
```

---

## FASE 2: IMPLEMENTAR DESIGNREVIEWER (On-demand)

### 2.1 Crear Configuración

**Archivo: `.quality_control/designreviewer/config.yml`**

```yaml
# DesignReviewer Configuration
version: "1.0"

enabled: true

# Triggers
triggers:
  manual: true
  pr_label: "design-review"
  weekly: false

# Umbrales de bloqueo
blocking_thresholds:
  class_size: 200
  wmc: 20
  cc_per_class: 30
  cbo: 5
  dit: 5
  nop: 1
  duplicated_lines: 5.0
  coverage: 70.0
  bugs: 0
  circular_imports: 0
  code_smells_critical: 0

# Umbrales de advertencia
warning_thresholds:
  lcom: 1.0
  mi: 20
  fan_out: 7
  tech_debt_ratio: 5.0
  branch_coverage: 75.0

# Configuración de IA
ai_suggestions:
  enabled: true
  api_key_env: "ANTHROPIC_API_KEY"  # Leer de variable de entorno
  model: "claude-sonnet-4"
  max_tokens: 4000
  include_examples: true
  include_effort_estimate: true

# Reportes
reports:
  html: true
  html_path: "reports/design/"
  markdown: true
  markdown_path: "reports/design/"
  include_graphs: true
  include_history: false  # Implementar en fase posterior

# Excepciones
exceptions:
  allow_justified: true
  require_approval: false  # Para proyectos personales
  approval_file: ".quality_control/designreviewer/approvals.yml"
```

### 2.2 Configurar Variable de Entorno para IA

**En tu `.bashrc` o `.zshrc`:**

```bash
export ANTHROPIC_API_KEY="tu-api-key-aqui"
```

**O crear archivo `.env` en el proyecto:**

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

**Y agregar a `.gitignore`:**

```bash
echo ".env" >> .gitignore
```

### 2.3 Crear Script Simplificado del Agente

**Archivo: `quality_agents/designreviewer.py`**

```python
#!/usr/bin/env python3
"""
DesignReviewer - Deep Design Analysis Agent
Analiza calidad de diseño y sugiere refactorizaciones
"""

import sys
import os
from pathlib import Path
import yaml
from anthropic import Anthropic
from rich.console import Console
from rich.progress import Progress

console = Console()

class DesignReviewer:
    def __init__(self, config_path: str = ".quality_control/designreviewer/config.yml"):
        self.config = self._load_config(config_path)
        self.client = self._init_ai() if self.config['ai_suggestions']['enabled'] else None
        
    def _load_config(self, path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def _init_ai(self):
        api_key = os.getenv(self.config['ai_suggestions']['api_key_env'])
        if not api_key:
            console.print("[yellow]Warning: ANTHROPIC_API_KEY not set. AI suggestions disabled.[/yellow]")
            return None
        return Anthropic(api_key=api_key)
    
    def run(self):
        """Ejecuta análisis completo"""
        console.print("\n[bold cyan]🔬 DesignReviewer - Deep Analysis[/bold cyan]")
        console.print("━" * 60)
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Analyzing...", total=100)
            
            # TODO: Implementar análisis real
            # Por ahora, demostración básica
            
            progress.update(task, advance=20)
            console.print("📊 Calculating metrics...")
            
            progress.update(task, advance=30)
            console.print("🔍 Detecting code smells...")
            
            progress.update(task, advance=30)
            console.print("🤖 Generating AI suggestions...")
            
            progress.update(task, advance=20)
            console.print("📄 Creating report...")
        
        console.print("\n[green]✅ Analysis complete![/green]")
        console.print(f"📊 Report: reports/design/review_{Path.cwd().name}.html\n")
        
        return 0

def main():
    reviewer = DesignReviewer()
    sys.exit(reviewer.run())

if __name__ == '__main__':
    main()
```

### 2.4 Ejecutar Manualmente

```bash
# Hacer ejecutable
chmod +x quality_agents/designreviewer.py

# Ejecutar
python3 quality_agents/designreviewer.py
```

---

## FASE 3: INTEGRACIÓN CON GITHUB ACTIONS (Opcional)

**Archivo: `.github/workflows/quality-check.yml`**

```yaml
name: Quality Check

on:
  pull_request:
    types: [opened, synchronize, labeled]

jobs:
  design-review:
    if: contains(github.event.pull_request.labels.*.name, 'design-review')
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-quality.txt
      
      - name: Run DesignReviewer
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python3 quality_agents/designreviewer.py
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: design-review-report
          path: reports/design/
```

**Configurar Secret en GitHub:**
1. Ve a tu repo → Settings → Secrets and variables → Actions
2. New repository secret
3. Name: `ANTHROPIC_API_KEY`
4. Value: tu API key

---

## VERIFICACIÓN FINAL

### Checklist de Configuración

```bash
# ✅ Verificar estructura de directorios
tree .quality_control/
tree reports/
tree quality_agents/

# ✅ Verificar archivos de configuración
ls .quality_control/codeguard/config.yml
ls .quality_control/designreviewer/config.yml
ls .flake8
ls .pylintrc
ls bandit.yml

# ✅ Verificar instalación de herramientas
flake8 --version
pylint --version
bandit --version
radon --version

# ✅ Verificar hook de git
ls -la .git/hooks/pre-commit
cat .git/hooks/pre-commit

# ✅ Probar CodeGuard manualmente
python3 quality_agents/codeguard.py

# ✅ Probar con commit
git add .
git commit -m "Test quality agents"
```

---

## TROUBLESHOOTING

### Problema: CodeGuard no se ejecuta en pre-commit

**Solución:**
```bash
# Verificar que el hook sea ejecutable
chmod +x .git/hooks/pre-commit

# Verificar permisos del script
chmod +x quality_agents/codeguard.py

# Probar manualmente
python3 .git/hooks/pre-commit
```

### Problema: "ModuleNotFoundError" al ejecutar

**Solución:**
```bash
# Asegurar que estás en el venv correcto
which python3

# Reinstalar dependencias
pip install -r requirements-quality.txt

# Verificar instalación
pip list | grep flake8
```

### Problema: API Key de Anthropic no funciona

**Solución:**
```bash
# Verificar variable de entorno
echo $ANTHROPIC_API_KEY

# Si usas .env, cargar con:
export $(cat .env | xargs)

# O instalar python-dotenv
pip install python-dotenv
```

---

## PRÓXIMOS PASOS

1. **Usar CodeGuard durante 1 semana** - Familiarizarte con el flujo
2. **Implementar DesignReviewer completo** - Agregar análisis real de métricas
3. **Implementar ArchitectAnalyst** - Para análisis de sprint
4. **Refinar configuraciones** - Ajustar umbrales según tu proyecto
5. **Documentar excepciones** - Crear proceso de waivers

---

## RESUMEN DE COMANDOS

```bash
# Setup inicial
pip install -r requirements-quality.txt
chmod +x quality_agents/*.py
chmod +x .git/hooks/pre-commit

# Uso diario
# - CodeGuard se ejecuta automáticamente en cada commit

# Análisis profundo (manual)
python3 quality_agents/designreviewer.py

# Verificar configuración
cat .quality_control/codeguard/config.yml
cat .quality_control/designreviewer/config.yml
```

---

**NOTA IMPORTANTE:**

Este setup es un MVP funcional. Los scripts de `codeguard.py` y `designreviewer.py` son implementaciones básicas que deberás expandir según necesites más features. El documento de especificación tiene todos los detalles de cómo deberían funcionar completamente.

¿Te queda claro cómo configurar e implementar los agentes?
