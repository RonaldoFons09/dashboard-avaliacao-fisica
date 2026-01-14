"""
Gráfico de Evolução - Componente visual para exibir histórico.

Este módulo contém funções para criar gráficos de linha usando Plotly,
mostrando a evolução de peso, perímetros e outros indicadores ao longo do tempo.
"""

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from servicos.analisador_perimetros import obter_nome_amigavel


def criar_grafico_evolucao_peso(avaliacoes: list[dict]) -> go.Figure:
    """
    Cria um gráfico de linha mostrando a evolução do peso.
    
    :param avaliacoes: Lista de avaliações ordenadas por data
    :return: Figura Plotly
    """
    if not avaliacoes:
        return go.Figure()
    
    datas = [a.get("data", "") for a in avaliacoes]
    pesos = [a.get("peso_kg", 0) for a in avaliacoes]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=datas,
        y=pesos,
        mode='lines+markers',
        name='Peso',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10, color='#667eea'),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)'
    ))
    
    fig.update_layout(
        title=dict(
            text="Evolução do Peso",
            font=dict(size=16, color='white')
        ),
        xaxis_title="Data",
        yaxis_title="Peso (kg)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=350,
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        )
    )
    
    return fig


def criar_grafico_evolucao_perimetro(
    avaliacoes: list[dict],
    chave_perimetro: str
) -> go.Figure:
    """
    Cria um gráfico de linha para um perímetro específico.
    
    :param avaliacoes: Lista de avaliações ordenadas por data
    :param chave_perimetro: Chave do perímetro a visualizar
    :return: Figura Plotly
    """
    if not avaliacoes:
        return go.Figure()
    
    datas = []
    valores = []
    
    for avaliacao in avaliacoes:
        perimetros = avaliacao.get("perimetros", {})
        valor = perimetros.get(chave_perimetro, 0)
        
        if valor > 0:
            datas.append(avaliacao.get("data", ""))
            valores.append(valor)
    
    nome_amigavel = obter_nome_amigavel(chave_perimetro)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=datas,
        y=valores,
        mode='lines+markers',
        name=nome_amigavel,
        line=dict(color='#2ecc71', width=3),
        marker=dict(size=10, color='#2ecc71')
    ))
    
    fig.update_layout(
        title=dict(
            text=f"Evolução: {nome_amigavel}",
            font=dict(size=16, color='white')
        ),
        xaxis_title="Data",
        yaxis_title="Medida (cm)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=350,
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        )
    )
    
    return fig


def criar_grafico_multiplos_perimetros(
    avaliacoes: list[dict],
    chaves_perimetros: list[str]
) -> go.Figure:
    """
    Cria um gráfico com múltiplos perímetros sobrepostos.
    
    :param avaliacoes: Lista de avaliações ordenadas por data
    :param chaves_perimetros: Lista de chaves dos perímetros a visualizar
    :return: Figura Plotly
    """
    if not avaliacoes:
        return go.Figure()
    
    cores = ['#667eea', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']
    
    fig = go.Figure()
    
    for indice, chave in enumerate(chaves_perimetros):
        datas = []
        valores = []
        
        for avaliacao in avaliacoes:
            perimetros = avaliacao.get("perimetros", {})
            valor = perimetros.get(chave, 0)
            
            if valor > 0:
                datas.append(avaliacao.get("data", ""))
                valores.append(valor)
        
        nome = obter_nome_amigavel(chave)
        cor = cores[indice % len(cores)]
        
        fig.add_trace(go.Scatter(
            x=datas,
            y=valores,
            mode='lines+markers',
            name=nome,
            line=dict(color=cor, width=2),
            marker=dict(size=8, color=cor)
        ))
    
    fig.update_layout(
        title=dict(
            text="Evolução dos Perímetros",
            font=dict(size=16, color='white')
        ),
        xaxis_title="Data",
        yaxis_title="Medida (cm)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        )
    )
    
    return fig


def criar_grafico_barras_variacao(variacoes: dict) -> go.Figure:
    """
    Cria um gráfico de barras mostrando variação entre duas avaliações.
    
    :param variacoes: Dicionário de variações retornado por calcular_variacao_entre_avaliacoes
    :return: Figura Plotly
    """
    if not variacoes:
        return go.Figure()
    
    nomes = []
    valores = []
    cores = []
    
    for chave, dados in variacoes.items():
        nomes.append(dados["nome"])
        valores.append(dados["diferenca_cm"])
        
        if dados["status"] == "aumento":
            cores.append("#2ecc71")
        elif dados["status"] == "reducao":
            cores.append("#e74c3c")
        else:
            cores.append("#95a5a6")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=nomes,
        y=valores,
        marker_color=cores,
        text=[f"{v:+.1f}" for v in valores],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=dict(
            text="Variação entre Avaliações (cm)",
            font=dict(size=16, color='white')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400,
        xaxis=dict(
            tickangle=-45,
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.3)'
        )
    )
    
    return fig


def renderizar_grafico_evolucao_peso(avaliacoes: list[dict]) -> None:
    """
    Renderiza o gráfico de evolução de peso no Streamlit.
    
    :param avaliacoes: Lista de avaliações
    """
    if len(avaliacoes) < 1:
        st.info("Necessário pelo menos 1 avaliação para visualizar evolução.")
        return
    
    fig = criar_grafico_evolucao_peso(avaliacoes)
    st.plotly_chart(fig, use_container_width=True)


def renderizar_grafico_evolucao_perimetro(
    avaliacoes: list[dict],
    chave_perimetro: str
) -> None:
    """
    Renderiza o gráfico de evolução de um perímetro no Streamlit.
    
    :param avaliacoes: Lista de avaliações
    :param chave_perimetro: Chave do perímetro
    """
    fig = criar_grafico_evolucao_perimetro(avaliacoes, chave_perimetro)
    st.plotly_chart(fig, use_container_width=True)
