"""
Quality Agents - Sistema de Control de Calidad en Tres Niveles

Agentes:
    - CodeGuard: Pre-commit, advertencias rápidas (< 5 segundos)
    - DesignReviewer: Review, análisis profundo (2-5 minutos)
    - ArchitectAnalyst: Sprint-end, análisis estratégico (10-30 minutos)
"""

__version__ = "0.1.0"

from .codeguard import CodeGuard
from .designreviewer import DesignReviewer
from .architectanalyst import ArchitectAnalyst

__all__ = ["CodeGuard", "DesignReviewer", "ArchitectAnalyst"]
