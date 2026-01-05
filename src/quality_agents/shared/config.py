"""
Configuración compartida entre agentes.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional

import yaml


@dataclass
class QualityConfig:
    """Configuración global del sistema de calidad."""

    # Rutas
    reports_dir: Path = field(default_factory=lambda: Path("reports"))
    db_path: Path = field(default_factory=lambda: Path(".quality_control/quality.db"))

    # Umbrales globales
    thresholds: Dict[str, float] = field(default_factory=lambda: {
        # Código
        "cyclomatic_complexity": 10,
        "function_lines": 20,
        "nesting_depth": 4,

        # Diseño
        "cbo": 5,
        "lcom": 1,
        "maintainability_index": 20,
        "wmc": 20,

        # Arquitectura
        "distance": 0.3,
        "layer_violations": 0,
        "dependency_cycles": 0,
    })

    # IA
    ai_enabled: bool = True
    ai_model: str = "claude-sonnet-4-20250514"

    @classmethod
    def from_yaml(cls, path: Path) -> "QualityConfig":
        """Carga configuración desde YAML."""
        if not path.exists():
            return cls()

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        config = cls()

        if "reports_dir" in data:
            config.reports_dir = Path(data["reports_dir"])
        if "db_path" in data:
            config.db_path = Path(data["db_path"])
        if "thresholds" in data:
            config.thresholds.update(data["thresholds"])
        if "ai_enabled" in data:
            config.ai_enabled = data["ai_enabled"]
        if "ai_model" in data:
            config.ai_model = data["ai_model"]

        return config


def load_config(config_path: Optional[Path] = None) -> QualityConfig:
    """
    Carga configuración buscando en ubicaciones estándar.

    Args:
        config_path: Ruta explícita (opcional)

    Returns:
        Configuración cargada
    """
    if config_path and config_path.exists():
        return QualityConfig.from_yaml(config_path)

    # Buscar en ubicaciones estándar
    standard_paths = [
        Path(".quality.yml"),
        Path(".quality.yaml"),
        Path("configs/quality.yml"),
        Path("quality.yml"),
    ]

    for path in standard_paths:
        if path.exists():
            return QualityConfig.from_yaml(path)

    return QualityConfig()
