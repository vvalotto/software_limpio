"""
Configuración para CodeGuard.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml


@dataclass
class CodeGuardConfig:
    """Configuración de CodeGuard."""

    # Umbrales
    min_pylint_score: float = 8.0
    max_cyclomatic_complexity: int = 10
    max_line_length: int = 100
    max_function_lines: int = 20

    # Verificaciones habilitadas
    check_pep8: bool = True
    check_pylint: bool = True
    check_security: bool = True
    check_complexity: bool = True
    check_types: bool = True
    check_imports: bool = True

    # Exclusiones
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "*.pyc",
        "__pycache__",
        ".venv",
        "venv",
        "migrations",
    ])

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

        return cls(**data) if data else cls()

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
            "check_pep8": self.check_pep8,
            "check_pylint": self.check_pylint,
            "check_security": self.check_security,
            "check_complexity": self.check_complexity,
            "check_types": self.check_types,
            "check_imports": self.check_imports,
            "exclude_patterns": self.exclude_patterns,
        }

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
