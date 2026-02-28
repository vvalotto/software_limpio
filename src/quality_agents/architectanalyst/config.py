"""
Configuración para ArchitectAnalyst.

Fecha de creación: 2026-02-28
Ticket: 1.4
"""

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

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
    """Configuración de IA para ArchitectAnalyst."""

    enabled: bool = False       # Opt-in por defecto
    max_tokens: int = 1500      # Mayor que DesignReviewer — análisis estratégico más extenso


@dataclass
class LayersConfig:
    """
    Configuración de arquitectura en capas.

    Declara las capas del sistema y sus dependencias permitidas.
    LayerViolationsAnalyzer (Fase 3) usa esta configuración para detectar imports
    que violan la dirección de dependencias.

    Ejemplo de configuración en pyproject.toml:

        [tool.architectanalyst.layers]
        domain = []
        application = ["domain"]
        infrastructure = ["application", "domain"]

    Con esta configuración, un import de `domain` hacia `application` sería CRITICAL.

    Attributes:
        rules: Mapeo de nombre de capa → lista de capas de las que puede depender.
               Si está vacío, LayerViolationsAnalyzer está efectivamente desactivado.
    """

    rules: Dict[str, List[str]] = field(default_factory=dict)

    def is_configured(self) -> bool:
        """Retorna True si hay reglas de capas definidas."""
        return bool(self.rules)


@dataclass
class ArchitectAnalystConfig:
    """
    Configuración de ArchitectAnalyst.

    Umbrales para las Métricas de Martin y configuración general.
    Los valores default corresponden a los umbrales definidos en el plan v0.3.0.
    """

    # --- Métricas de Martin ---
    # Ca (Afferent Coupling) y Ce (Efferent Coupling): solo informativos, sin umbral
    # I (Instability) = Ce / (Ca + Ce)
    max_instability: float = 0.8        # I > 0.8 → WARNING
    # A (Abstractness): solo informativo, sin umbral
    # D (Distance from Main Sequence) = |A + I - 1|
    max_distance_warning: float = 0.3   # D > 0.3 → WARNING
    max_distance_critical: float = 0.5  # D > 0.5 → CRITICAL

    # --- Ciclos y capas: siempre CRITICAL si se detectan (no configurables) ---
    # dependency_cycles = 0
    # layer_violations = 0

    # --- Persistencia histórica ---
    db_path: str = ".quality_control/architecture.db"

    # --- Exclusiones ---
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "__pycache__",
        ".venv",
        "venv",
        "migrations",
        "test_",
        "conftest",
        "dist",
        "build",
    ])

    # --- Subsecciones ---
    ai: AIConfig = field(default_factory=AIConfig)
    layers: LayersConfig = field(default_factory=LayersConfig)

    @classmethod
    def from_pyproject_toml(cls, path: Path) -> "ArchitectAnalystConfig":
        """
        Carga configuración desde pyproject.toml.

        Lee la sección [tool.architectanalyst] y opcionalmente
        [tool.architectanalyst.ai] y [tool.architectanalyst.layers].

        Args:
            path: Ruta al archivo pyproject.toml.

        Returns:
            Instancia de ArchitectAnalystConfig.

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

        tool_config = data.get("tool", {}).get("architectanalyst", {})

        if not tool_config:
            return cls()

        # Extraer sub-secciones antes de pasar el resto al dataclass
        ai_data = tool_config.pop("ai", {})
        layers_data = tool_config.pop("layers", {})

        ai_config = AIConfig(**ai_data) if ai_data else AIConfig()
        layers_config = LayersConfig(rules=layers_data) if layers_data else LayersConfig()

        config = cls(**tool_config)
        config.ai = ai_config
        config.layers = layers_config
        return config


def load_config(
    config_path: Optional[Path] = None,
    project_root: Optional[Path] = None,
) -> ArchitectAnalystConfig:
    """
    Carga configuración buscando en ubicaciones estándar.

    Orden de búsqueda:
    1. config_path explícito (si se provee)
    2. pyproject.toml en project_root → [tool.architectanalyst]
    3. Defaults internos

    Args:
        config_path: Ruta explícita a archivo de configuración (opcional).
        project_root: Directorio raíz del proyecto (default: directorio actual).

    Returns:
        Instancia de ArchitectAnalystConfig cargada.
    """
    if project_root is None:
        project_root = Path.cwd()

    # 1. Config path explícito
    if config_path is not None:
        if not config_path.exists():
            logger.warning(f"Archivo de config no encontrado: {config_path}, usando defaults")
            return ArchitectAnalystConfig()
        if config_path.suffix == ".toml":
            logger.info(f"Cargando config desde: {config_path} (TOML)")
            return ArchitectAnalystConfig.from_pyproject_toml(config_path)
        logger.warning(f"Formato de config no soportado: {config_path}, usando defaults")
        return ArchitectAnalystConfig()

    # 2. Buscar pyproject.toml en project_root
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            if tomllib is not None:
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                if "tool" in data and "architectanalyst" in data["tool"]:
                    logger.info(
                        f"Cargando config desde: {pyproject_path} → [tool.architectanalyst]"
                    )
                    return ArchitectAnalystConfig.from_pyproject_toml(pyproject_path)
        except Exception as e:
            logger.warning(f"Error leyendo pyproject.toml: {e}, usando defaults")

    # 3. Defaults
    logger.info("No se encontró configuración, usando defaults")
    return ArchitectAnalystConfig()
