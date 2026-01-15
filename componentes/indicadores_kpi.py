"""
Indicadores KPI - Componente visual para exibir métricas principais.

Este módulo contém funções para renderizar cards de KPIs usando st.metric
com cores e formatações customizadas.
"""

import streamlit as st
from servicos.calculadora_corporal import (
    calcular_imc,
    classificar_imc,
    obter_cor_imc,
    calcular_tmb,
    calcular_gasto_calorico_diario,
    calcular_idade,
    calcular_gordura_pollock7,
    classificar_percentual_gordura
)


def renderizar_kpis_principais(cliente: dict, avaliacao: dict) -> None:
    """
    Renderiza os principais indicadores em uma linha de cards.
    
    :param cliente: Dicionário com dados do cliente
    :param avaliacao: Dicionário com dados da última avaliação
    """
    if not avaliacao:
        st.warning("Sem dados de avaliação para exibir.")
        return
    
    peso = avaliacao.get("peso_kg", 0)
    altura = avaliacao.get("altura_cm", 0)
    nivel_atividade = avaliacao.get("nivel_atividade", "Sedentário")
    dobras = avaliacao.get("dobras_cutaneas", {})
    
    genero = cliente.get("genero", "Masculino")
    data_nascimento = cliente.get("data_nascimento", "")
    idade = calcular_idade(data_nascimento) if data_nascimento else 25
    
    # Cálculos
    imc = calcular_imc(peso, altura)
    classificacao_imc = classificar_imc(imc)
    tmb = calcular_tmb(peso, altura, idade, genero)
    gasto_diario = calcular_gasto_calorico_diario(tmb, nivel_atividade)
    
    # Calcula % gordura se houver dobras
    percentual_gordura = None
    classificacao_gordura = None
    if dobras and any(v > 0 for v in dobras.values()):
        resultado_gordura = calcular_gordura_pollock7(dobras, idade, genero)
        percentual_gordura = resultado_gordura["percentual_gordura"]
        classificacao_gordura = resultado_gordura["classificacao"]
    
    # Renderização - 5 colunas se tiver gordura, 4 se não tiver
    if percentual_gordura is not None:
        col1, col2, col3, col4, col5 = st.columns(5)
    else:
        col1, col2, col3, col4 = st.columns(4)
        col5 = None
    
    with col1:
        st.metric(
            label="⚖️ Peso",
            value=f"{peso} kg"
        )
    
    with col2:
        st.metric(
            label="📊 IMC",
            value=f"{imc}",
            help=classificacao_imc
        )
    
    with col3:
        st.metric(
            label="🔥 TMB",
            value=f"{tmb:.0f} kcal",
            help="Taxa Metabólica Basal"
        )
    
    with col4:
        st.metric(
            label="⚡ Gasto Diário",
            value=f"{gasto_diario:.0f} kcal",
            help=f"Nível: {nivel_atividade}"
        )
    
    if col5 is not None:
        with col5:
            st.metric(
                label="🔥 % Gordura",
                value=f"{percentual_gordura:.1f}%",
                help=classificacao_gordura
            )


def renderizar_kpi_imc_detalhado(peso: float, altura: float) -> None:
    """
    Renderiza um card de IMC com mais detalhes e barra visual.
    
    :param peso: Peso em kg
    :param altura: Altura em cm
    """
    imc = calcular_imc(peso, altura)
    classificacao = classificar_imc(imc)
    cor = obter_cor_imc(imc)
    
    st.markdown(f"""
    <div style="
        background-color: #1e1e1e;
        border-left: 5px solid {cor};
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    ">
        <div style="font-size: 0.9em; color: #888;">Índice de Massa Corporal</div>
        <div style="font-size: 2em; font-weight: bold; color: {cor};">{imc}</div>
        <div style="font-size: 1.1em; color: white;">{classificacao}</div>
    </div>
    """, unsafe_allow_html=True)


def renderizar_kpis_evolucao(avaliacao_anterior: dict, avaliacao_atual: dict) -> None:
    """
    Renderiza KPIs com deltas de evolução entre duas avaliações.
    
    :param avaliacao_anterior: Avaliação mais antiga
    :param avaliacao_atual: Avaliação mais recente
    """
    if not avaliacao_anterior or not avaliacao_atual:
        st.warning("Necessário pelo menos 2 avaliações para comparar.")
        return
    
    peso_anterior = avaliacao_anterior.get("peso_kg", 0)
    peso_atual = avaliacao_atual.get("peso_kg", 0)
    delta_peso = peso_atual - peso_anterior
    
    altura = avaliacao_atual.get("altura_cm", 0)
    imc_anterior = calcular_imc(peso_anterior, altura)
    imc_atual = calcular_imc(peso_atual, altura)
    delta_imc = imc_atual - imc_anterior
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="⚖️ Peso",
            value=f"{peso_atual} kg",
            delta=f"{delta_peso:+.1f} kg"
        )
    
    with col2:
        st.metric(
            label="📊 IMC",
            value=f"{imc_atual}",
            delta=f"{delta_imc:+.2f}"
        )


def renderizar_card_caloria(titulo: str, valor: float, icone: str, cor: str = "#667eea") -> None:
    """
    Renderiza um card individual de caloria.
    
    :param titulo: Título do card
    :param valor: Valor em kcal
    :param icone: Emoji para o ícone
    :param cor: Cor do gradiente
    """
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {cor} 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        color: white;
    ">
        <div style="font-size: 1.5em;">{icone}</div>
        <div style="font-size: 0.9em; opacity: 0.8;">{titulo}</div>
        <div style="font-size: 1.5em; font-weight: bold;">{valor:.0f} kcal</div>
    </div>
    """, unsafe_allow_html=True)
