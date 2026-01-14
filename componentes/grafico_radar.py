"""
Gráfico Radar - Componente visual para exibir perímetros corporais.

Este módulo contém funções para criar gráficos radar usando Plotly,
mostrando os perímetros corporais de forma visual.
"""

import plotly.graph_objects as go
import streamlit as st
from servicos.analisador_perimetros import (
    preparar_dados_grafico_radar,
    preparar_comparacao_radar
)


def criar_grafico_radar(perimetros: dict, titulo: str = "Perímetros Corporais") -> go.Figure:
    """
    Cria um gráfico radar com os perímetros corporais.
    
    :param perimetros: Dicionário com as medidas
    :param titulo: Título do gráfico
    :return: Figura Plotly
    """
    dados = preparar_dados_grafico_radar(perimetros)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=dados["valores"],
        theta=dados["categorias"],
        fill='toself',
        name='Atual',
        line_color='#667eea',
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(dados["valores"]) * 1.2] if dados["valores"] else [0, 100]
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        title=dict(
            text=titulo,
            font=dict(size=16, color='white')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=450
    )
    
    return fig


def criar_grafico_radar_comparativo(
    perimetros_anterior: dict,
    perimetros_atual: dict,
    label_anterior: str = "Anterior",
    label_atual: str = "Atual"
) -> go.Figure:
    """
    Cria um gráfico radar comparando duas avaliações.
    
    :param perimetros_anterior: Perímetros da avaliação mais antiga
    :param perimetros_atual: Perímetros da avaliação mais recente
    :param label_anterior: Label para a série anterior
    :param label_atual: Label para a série atual
    :return: Figura Plotly
    """
    dados = preparar_comparacao_radar(perimetros_anterior, perimetros_atual)
    
    fig = go.Figure()
    
    # Série anterior
    fig.add_trace(go.Scatterpolar(
        r=dados["valores_anterior"],
        theta=dados["categorias"],
        fill='toself',
        name=label_anterior,
        line_color='#e74c3c',
        fillcolor='rgba(231, 76, 60, 0.2)'
    ))
    
    # Série atual
    fig.add_trace(go.Scatterpolar(
        r=dados["valores_atual"],
        theta=dados["categorias"],
        fill='toself',
        name=label_atual,
        line_color='#2ecc71',
        fillcolor='rgba(46, 204, 113, 0.2)'
    ))
    
    # Determinar range máximo
    todos_valores = dados["valores_anterior"] + dados["valores_atual"]
    range_max = max(todos_valores) * 1.2 if todos_valores else 100
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, range_max]
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        title=dict(
            text="Comparação de Perímetros",
            font=dict(size=16, color='white')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig


def renderizar_grafico_radar(perimetros: dict, titulo: str = "Perímetros Corporais") -> None:
    """
    Renderiza o gráfico radar no Streamlit.
    
    :param perimetros: Dicionário com as medidas
    :param titulo: Título do gráfico
    """
    if not perimetros or all(v == 0 for v in perimetros.values()):
        st.info("Sem dados de perímetros para exibir.")
        return
    
    fig = criar_grafico_radar(perimetros, titulo)
    st.plotly_chart(fig, use_container_width=True)


def renderizar_grafico_radar_comparativo(
    perimetros_anterior: dict,
    perimetros_atual: dict,
    data_anterior: str = "",
    data_atual: str = ""
) -> None:
    """
    Renderiza o gráfico radar comparativo no Streamlit.
    
    :param perimetros_anterior: Perímetros da avaliação mais antiga
    :param perimetros_atual: Perímetros da avaliação mais recente
    :param data_anterior: Data da avaliação anterior
    :param data_atual: Data da avaliação atual
    """
    label_anterior = f"Avaliação {data_anterior}" if data_anterior else "Anterior"
    label_atual = f"Avaliação {data_atual}" if data_atual else "Atual"
    
    fig = criar_grafico_radar_comparativo(
        perimetros_anterior,
        perimetros_atual,
        label_anterior,
        label_atual
    )
    
    st.plotly_chart(fig, use_container_width=True)
