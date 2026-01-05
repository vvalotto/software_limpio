"""
CodeGuard - Agente de Pre-commit

Ejecuta verificaciones rápidas (< 5 segundos) antes de cada commit.
Solo advierte, nunca bloquea.
"""

from .agent import CodeGuard

__all__ = ["CodeGuard"]
