"""
Integración con Claude API para sugerencias inteligentes.
"""

from typing import List, Optional

from .agent import ReviewResult


class AIAssistant:
    """
    Asistente de IA para generar sugerencias de mejora.

    Usa Claude API para analizar código y generar
    sugerencias contextualizadas.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el asistente de IA.

        Args:
            api_key: API key de Anthropic (usa env var si no se provee)
        """
        self.api_key = api_key
        self._client: Optional[object] = None

    def _get_client(self) -> object:
        """Obtiene cliente de Anthropic (lazy initialization)."""
        if self._client is None:
            try:
                import os

                import anthropic

                key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
                if key:
                    self._client = anthropic.Anthropic(api_key=key)
            except ImportError:
                pass

        return self._client

    def generate_suggestions(
        self,
        results: List[ReviewResult],
        code_context: str
    ) -> List[str]:
        """
        Genera sugerencias de mejora basadas en los resultados.

        Args:
            results: Resultados del análisis de diseño
            code_context: Código relevante para contexto

        Returns:
            Lista de sugerencias generadas por IA
        """
        client = self._get_client()
        if not client:
            return []

        # TODO: Implementar llamada a Claude API
        return []

    def explain_metric(self, metric_name: str, value: float, threshold: float) -> str:
        """
        Genera explicación de una métrica y cómo mejorarla.

        Args:
            metric_name: Nombre de la métrica
            value: Valor actual
            threshold: Umbral recomendado

        Returns:
            Explicación generada por IA
        """
        client = self._get_client()
        if not client:
            return f"{metric_name}: {value} (umbral: {threshold})"

        # TODO: Implementar llamada a Claude API
        return ""
