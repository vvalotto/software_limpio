"""
Módulo compartido entre agentes.
"""

from .config import QualityConfig, load_config
from .reporting import format_result, generate_summary
from .verifiable import ExecutionContext, Verifiable

__all__ = [
    "load_config",
    "QualityConfig",
    "format_result",
    "generate_summary",
    "ExecutionContext",
    "Verifiable",
]
