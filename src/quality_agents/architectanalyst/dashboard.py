"""
Dashboard interactivo para ArchitectAnalyst.
"""

from pathlib import Path
from typing import List, Dict, Any

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_metrics_dashboard(
    metrics_history: Dict[str, List[Dict[str, Any]]],
    output_path: Path
) -> None:
    """
    Crea dashboard HTML interactivo con Plotly.

    Args:
        metrics_history: Histórico de métricas
        output_path: Ruta donde guardar el dashboard
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Instabilidad (I)",
            "Distancia de Secuencia Principal (D)",
            "Acoplamiento (Ca/Ce)",
            "Violaciones de Capa"
        )
    )

    # TODO: Agregar trazas para cada métrica

    fig.update_layout(
        title="Dashboard de Arquitectura - Software Limpio",
        showlegend=True,
        height=800
    )

    fig.write_html(str(output_path))


def create_dependency_graph(
    dependencies: Dict[str, List[str]],
    output_path: Path
) -> None:
    """
    Crea grafo de dependencias interactivo.

    Args:
        dependencies: Diccionario de dependencias
        output_path: Ruta donde guardar el grafo
    """
    # TODO: Implementar con plotly network graph
    pass


def create_trend_chart(
    metric_name: str,
    values: List[float],
    timestamps: List[str],
    threshold: float
) -> go.Figure:
    """
    Crea gráfico de tendencia para una métrica.

    Args:
        metric_name: Nombre de la métrica
        values: Valores históricos
        timestamps: Timestamps correspondientes
        threshold: Umbral de referencia

    Returns:
        Figura de Plotly
    """
    fig = go.Figure()

    # Línea de valores
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=values,
        mode='lines+markers',
        name=metric_name
    ))

    # Línea de umbral
    fig.add_hline(
        y=threshold,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Umbral: {threshold}"
    )

    fig.update_layout(
        title=f"Tendencia: {metric_name}",
        xaxis_title="Fecha",
        yaxis_title="Valor"
    )

    return fig
