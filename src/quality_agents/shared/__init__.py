"""
Módulo compartido entre agentes.
"""

from .config import load_config, QualityConfig
from .reporting import format_result, generate_summary

__all__ = ["load_config", "QualityConfig", "format_result", "generate_summary"]
