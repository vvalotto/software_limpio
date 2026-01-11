"""
DesignReviewer - Agente de Review

Ejecuta análisis profundo (2-5 minutos) durante revisión de código.
Puede bloquear si encuentra problemas críticos.
"""

from .agent import DesignReviewer

__all__ = ["DesignReviewer"]
