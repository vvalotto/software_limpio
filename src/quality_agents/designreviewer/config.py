"""
Configuración para DesignReviewer.

Fecha de creación: 2026-02-19
Ticket: 1.5
"""

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

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
    """Configuración de IA para DesignReviewer."""

    enabled: bool = False  # Opt-in por defecto
    suggest_refactoring: bool = True
    max_tokens: int = 800


@dataclass
class DesignReviewerConfig:
    """
    Configuración de DesignReviewer.

    Umbrales por métrica de diseño. Todos los valores son los defaults
    recomendados por la literatura de métricas OO.
    """

    # Acoplamiento
    max_cbo: int = 5       # Coupling Between Objects
    max_fan_out: int = 7   # Fan-Out de módulos importados

    # Herencia
    max_dit: int = 5       # Depth of Inheritance Tree
    max_nop: int = 1       # Number of Parents (herencia múltiple)

    # Cohesión
    max_lcom: int = 1      # Lack of Cohesion of Methods

    # Complejidad de clase
    max_wmc: int = 20      # Weighted Methods per Class

    # Exclusiones
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "__pycache__",
        ".venv",
        "venv",
        "migrations",
        "test_",
        "conftest",
    ])

    # Configuración de IA
    ai: AIConfig = field(default_factory=AIConfig)

    @classmethod
    def from_pyproject_toml(cls, path: Path) -> "DesignReviewerConfig":
        """
        Carga configuración desde pyproject.toml.

        Lee la sección [tool.designreviewer] y opcionalmente [tool.designreviewer.ai].

        Args:
            path: Ruta al archivo pyproject.toml.

        Returns:
            Instancia de DesignReviewerConfig.

        Raises:
            ImportError: Si tomllib/tomli no está disponible.
            FileNotFoundError: Si el archivo no existe.
        """
        if tomllib is None:
            raise ImportError(
                "tomllib/tomli es requerido para leer pyproject.toml. "
                "Instalá tomli para Python < 3.11: pip install tomli"
            )

        if not path.exists():
            raise FileNotFoundError(f"pyproject.toml no encontrado en {path}")

        with open(path, "rb") as f:
            data = tomllib.load(f)

        tool_config = data.get("tool", {}).get("designreviewer", {})

        if not tool_config:
            return cls()

        # Extraer sub-sección de IA
        ai_data = tool_config.pop("ai", {})
        ai_config = AIConfig(**ai_data) if ai_data else AIConfig()

        config = cls(**tool_config)
        config.ai = ai_config
        return config


def load_config(
    config_path: Optional[Path] = None,
    project_root: Optional[Path] = None,
) -> DesignReviewerConfig:
    """
    Carga configuración buscando en ubicaciones estándar.

    Orden de búsqueda:
    1. config_path explícito (si se provee)
    2. pyproject.toml en project_root → [tool.designreviewer]
    3. Defaults internos

    Args:
        config_path: Ruta explícita a archivo de configuración (opcional).
        project_root: Directorio raíz del proyecto (default: directorio actual).

    Returns:
        Instancia de DesignReviewerConfig cargada.
    """
    if project_root is None:
        project_root = Path.cwd()

    # 1. Config path explícito
    if config_path is not None:
        if not config_path.exists():
            logger.warning(f"Archivo de config no encontrado: {config_path}, usando defaults")
            return DesignReviewerConfig()
        if config_path.suffix == ".toml":
            logger.info(f"Cargando config desde: {config_path} (TOML)")
            return DesignReviewerConfig.from_pyproject_toml(config_path)
        logger.warning(f"Formato de config no soportado: {config_path}, usando defaults")
        return DesignReviewerConfig()

    # 2. Buscar pyproject.toml en project_root
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            if tomllib is not None:
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                if "tool" in data and "designreviewer" in data["tool"]:
                    logger.info(
                        f"Cargando config desde: {pyproject_path} → [tool.designreviewer]"
                    )
                    return DesignReviewerConfig.from_pyproject_toml(pyproject_path)
        except Exception as e:
            logger.warning(f"Error leyendo pyproject.toml: {e}, usando defaults")

    # 3. Defaults
    logger.info("No se encontró configuración, usando defaults")
    return DesignReviewerConfig()
