"""
Configuración para CodeGuard.
"""

import dataclasses
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml

logger = logging.getLogger(__name__)


def _filter_fields(cls: type, data: dict) -> dict:
    """Filtra un dict dejando solo las claves que son campos del dataclass."""
    known = {f.name for f in dataclasses.fields(cls)}
    for key in set(data) - known:
        logger.warning(f"[tool.codeguard] clave desconocida ignorada: '{key}'")
    return {k: v for k, v in data.items() if k in known}


# Python 3.11+ tiene tomllib en stdlib, versiones anteriores usan tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


@dataclass
class AIConfig:
    """Configuración de IA para CodeGuard."""

    enabled: bool = False  # Opt-in por defecto
    explain_errors: bool = True
    suggest_fixes: bool = True
    max_tokens: int = 500


@dataclass
class ChecksConfig:
    """
    Toggles para habilitar/deshabilitar checks individuales de CodeGuard.

    Configurable desde pyproject.toml con la sección [tool.codeguard.checks]
    o desde YAML con la clave ``checks``.

    Example::

        [tool.codeguard.checks]
        pep8 = false
        security = true
    """

    pep8: bool = True
    pylint: bool = True
    security: bool = True
    complexity: bool = True
    types: bool = True
    imports: bool = True


@dataclass
class CodeGuardConfig:
    """Configuración de CodeGuard."""

    # Umbrales
    min_pylint_score: float = 8.0
    max_cyclomatic_complexity: int = 10
    max_line_length: int = 100
    max_function_lines: int = 20

    # Exclusiones
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "*.pyc",
        "__pycache__",
        ".venv",
        "venv",
        "migrations",
    ])

    # Toggles de checks
    checks: ChecksConfig = field(default_factory=ChecksConfig)

    # Configuración de IA
    ai: AIConfig = field(default_factory=AIConfig)

    @classmethod
    def from_yaml(cls, path: Path) -> "CodeGuardConfig":
        """
        Carga configuración desde archivo YAML.

        Args:
            path: Ruta al archivo YAML

        Returns:
            Instancia de CodeGuardConfig
        """
        with open(path) as f:
            data = yaml.safe_load(f)

        if not data:
            return cls()

        # Extraer sub-secciones antes de pasar el resto al dataclass
        ai_data = data.pop("ai", {})
        checks_data = data.pop("checks", {})
        ai_config = AIConfig(**_filter_fields(AIConfig, ai_data)) if ai_data else AIConfig()
        checks_config = ChecksConfig(**_filter_fields(ChecksConfig, checks_data)) if checks_data else ChecksConfig()

        config = cls(**_filter_fields(cls, data))
        config.ai = ai_config
        config.checks = checks_config

        return config

    @classmethod
    def from_pyproject_toml(cls, path: Path) -> "CodeGuardConfig":
        """
        Carga configuración desde pyproject.toml.

        Lee la sección [tool.codeguard] y opcionalmente [tool.codeguard.ai]

        Args:
            path: Ruta al archivo pyproject.toml

        Returns:
            Instancia de CodeGuardConfig

        Raises:
            ImportError: Si tomllib/tomli no está disponible
            FileNotFoundError: Si el archivo no existe
        """
        if tomllib is None:
            raise ImportError(
                "tomllib/tomli is required to read pyproject.toml. "
                "Install tomli for Python < 3.11: pip install tomli"
            )

        if not path.exists():
            raise FileNotFoundError(f"pyproject.toml not found at {path}")

        with open(path, "rb") as f:
            data = tomllib.load(f)

        # Buscar sección [tool.codeguard]
        tool_config = data.get("tool", {}).get("codeguard", {})

        if not tool_config:
            # No hay configuración de codeguard, retornar defaults
            return cls()

        # Extraer sub-secciones antes de pasar el resto al dataclass
        ai_config_data = tool_config.pop("ai", {})
        checks_data = tool_config.pop("checks", {})
        ai_config = AIConfig(**_filter_fields(AIConfig, ai_config_data)) if ai_config_data else AIConfig()
        checks_config = ChecksConfig(**_filter_fields(ChecksConfig, checks_data)) if checks_data else ChecksConfig()

        config = cls(**_filter_fields(cls, tool_config))
        config.ai = ai_config
        config.checks = checks_config

        return config

    def to_yaml(self, path: Path) -> None:
        """
        Guarda configuración a archivo YAML.

        Args:
            path: Ruta donde guardar el archivo
        """
        data = {
            "min_pylint_score": self.min_pylint_score,
            "max_cyclomatic_complexity": self.max_cyclomatic_complexity,
            "max_line_length": self.max_line_length,
            "max_function_lines": self.max_function_lines,
            "exclude_patterns": self.exclude_patterns,
            "checks": {
                "pep8": self.checks.pep8,
                "pylint": self.checks.pylint,
                "security": self.checks.security,
                "complexity": self.checks.complexity,
                "types": self.checks.types,
                "imports": self.checks.imports,
            },
            "ai": {
                "enabled": self.ai.enabled,
                "explain_errors": self.ai.explain_errors,
                "suggest_fixes": self.ai.suggest_fixes,
                "max_tokens": self.ai.max_tokens,
            },
        }

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)


def load_config(config_path: Optional[Path] = None, project_root: Optional[Path] = None) -> CodeGuardConfig:
    """
    Carga configuración buscando en ubicaciones estándar.

    Orden de búsqueda:
    1. config_path explícito (si se provee)
    2. pyproject.toml en project_root → [tool.codeguard]
    3. .codeguard.yml en project_root
    4. Defaults internos

    Args:
        config_path: Ruta explícita a archivo de configuración (opcional)
        project_root: Directorio raíz del proyecto (default: directorio actual)

    Returns:
        Instancia de CodeGuardConfig cargada

    Examples:
        >>> # Buscar automáticamente
        >>> config = load_config()

        >>> # Con ruta explícita
        >>> config = load_config(Path("custom.yml"))

        >>> # Buscar en directorio específico
        >>> config = load_config(project_root=Path("/path/to/project"))
    """
    if project_root is None:
        project_root = Path.cwd()

    # 1. Si se provee config_path explícito, usarlo
    if config_path is not None:
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return CodeGuardConfig()

        # Determinar formato por extensión
        if config_path.suffix in [".toml"]:
            logger.info(f"Loading config from: {config_path} (TOML)")
            return CodeGuardConfig.from_pyproject_toml(config_path)
        elif config_path.suffix in [".yml", ".yaml"]:
            logger.info(f"Loading config from: {config_path} (YAML)")
            return CodeGuardConfig.from_yaml(config_path)
        else:
            logger.warning(f"Unknown config format: {config_path}, using defaults")
            return CodeGuardConfig()

    # 2. Buscar pyproject.toml en project_root
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            config = CodeGuardConfig.from_pyproject_toml(pyproject_path)
            # Verificar si realmente tiene configuración de codeguard
            # (from_pyproject_toml retorna defaults si no hay [tool.codeguard])
            with open(pyproject_path, "rb") as f:
                if tomllib is not None:
                    data = tomllib.load(f)
                    if "tool" in data and "codeguard" in data["tool"]:
                        logger.info(f"Loading config from: {pyproject_path} → [tool.codeguard]")
                        return config
        except (ImportError, FileNotFoundError):
            pass

    # 3. Buscar .codeguard.yml en project_root
    yml_path = project_root / ".codeguard.yml"
    if yml_path.exists():
        logger.info(f"Loading config from: {yml_path} (YAML fallback)")
        return CodeGuardConfig.from_yaml(yml_path)

    # 4. No se encontró configuración, usar defaults
    logger.info("No config file found, using defaults")
    return CodeGuardConfig()
