"""
Página Histórico - Visualização de evolução e comparações.

Esta página permite visualizar o histórico de avaliações do cliente,
gráficos de evolução e comparações entre diferentes datas.
Inclui comparação de perímetros e dobras cutâneas (Pollock 7).
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dados.gerenciador_clientes import buscar_cliente_por_id
from dados.gerenciador_avaliacoes import (
    obter_historico_avaliacoes,
    listar_datas_avaliacoes,
    obter_avaliacao_por_data,
    obter_ultima_avaliacao
)
from componentes.grafico_evolucao import (
    renderizar_grafico_evolucao_peso,
    criar_grafico_evolucao_perimetro,
    criar_grafico_barras_variacao
)
from componentes.grafico_radar import renderizar_grafico_radar_comparativo
from componentes.indicadores_kpi import renderizar_kpis_evolucao
from servicos.analisador_perimetros import (
    calcular_variacao_entre_avaliacoes,
    analisar_simetria_completa,
    NOMES_PERIMETROS
)
from servicos.calculadora_corporal import (
    calcular_imc,
    calcular_idade,
    calcular_gordura_pollock7,
    calcular_massas_corporais
)


# Nomes amigáveis para as dobras cutâneas
NOMES_DOBRAS = {
    "peitoral": "Peitoral",
    "axilar_media": "Axilar Média",
    "triceps": "Tríceps",
    "subescapular": "Subescapular",
    "abdominal": "Abdominal",
    "suprailiaca": "Suprailíaca",
    "coxa": "Coxa"
}


def renderizar_tabela_historico(avaliacoes: list[dict]) -> None:
    """
    Renderiza uma tabela com o histórico de avaliações.
    
    :param avaliacoes: Lista de avaliações ordenadas por data
    """
    if not avaliacoes:
        st.info("Nenhuma avaliação registrada.")
        return
    
    dados = []
    for avaliacao in avaliacoes:
        peso = avaliacao.get("peso_kg", 0)
        altura = avaliacao.get("altura_cm", 0)
        imc = calcular_imc(peso, altura)
        
        dados.append({
            "Data": avaliacao.get("data", ""),
            "Peso (kg)": peso,
            "Altura (cm)": altura,
            "IMC": imc,
            "Nível Atividade": avaliacao.get("nivel_atividade", "")
        })
    
    df = pd.DataFrame(dados)
    st.dataframe(df, use_container_width=True, hide_index=True)


def renderizar_comparacao_avaliacoes(cliente_id: str) -> None:
    """
    Renderiza a seção de comparação entre duas avaliações.
    
    :param cliente_id: ID do cliente
    """
    st.markdown("### 🔄 Comparar Avaliações")
    
    datas = listar_datas_avaliacoes(cliente_id)
    
    if len(datas) < 2:
        st.info("Necessário pelo menos 2 avaliações para comparar.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        data_anterior = st.selectbox(
            "Avaliação Anterior",
            options=datas,
            index=0,
            key="data_anterior"
        )
    
    with col2:
        data_atual = st.selectbox(
            "Avaliação Atual",
            options=datas,
            index=len(datas) - 1,
            key="data_atual"
        )
    
    if data_anterior == data_atual:
        st.warning("Selecione datas diferentes para comparar.")
        return
    
    avaliacao_anterior = obter_avaliacao_por_data(cliente_id, data_anterior)
    avaliacao_atual = obter_avaliacao_por_data(cliente_id, data_atual)
    
    if not avaliacao_anterior or not avaliacao_atual:
        st.error("Erro ao carregar avaliações.")
        return
    
    # KPIs de evolução
    st.markdown("#### 📊 Evolução de Peso e IMC")
    renderizar_kpis_evolucao(avaliacao_anterior, avaliacao_atual)
    
    st.divider()
    
    # Gráfico radar comparativo
    st.markdown("#### 📐 Comparação de Perímetros")
    perimetros_anterior = avaliacao_anterior.get("perimetros", {})
    perimetros_atual = avaliacao_atual.get("perimetros", {})
    
    renderizar_grafico_radar_comparativo(
        perimetros_anterior,
        perimetros_atual,
        data_anterior,
        data_atual
    )
    
    # Tabela de variações
    st.markdown("#### 📈 Variação Detalhada")
    variacoes = calcular_variacao_entre_avaliacoes(perimetros_anterior, perimetros_atual)
    
    if variacoes:
        fig = criar_grafico_barras_variacao(variacoes)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        dados_tabela = []
        for chave, dados in variacoes.items():
            dados_tabela.append({
                "Medida": dados["nome"],
                "Anterior (cm)": dados["anterior"],
                "Atual (cm)": dados["atual"],
                "Variação (cm)": f"{dados['diferenca_cm']:+.1f}",
                "Variação (%)": f"{dados['diferenca_percentual']:+.1f}%"
            })
        
        df = pd.DataFrame(dados_tabela)
        st.dataframe(df, use_container_width=True, hide_index=True)


def renderizar_comparacao_dobras(cliente_id: str, cliente: dict) -> None:
    """
    Renderiza a seção de comparação de dobras cutâneas.
    
    :param cliente_id: ID do cliente
    :param cliente: Dicionário com dados do cliente
    """
    st.markdown("### 📐 Comparação de Dobras Cutâneas")
    
    datas = listar_datas_avaliacoes(cliente_id)
    genero = cliente.get("genero", "Masculino")
    data_nascimento = cliente.get("data_nascimento", "")
    idade = calcular_idade(data_nascimento) if data_nascimento else 25
    
    if len(datas) < 2:
        st.info("Necessário pelo menos 2 avaliações para comparar.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        data_anterior = st.selectbox(
            "Avaliação Anterior",
            options=datas,
            index=0,
            key="dobras_data_anterior"
        )
    
    with col2:
        data_atual = st.selectbox(
            "Avaliação Atual",
            options=datas,
            index=len(datas) - 1,
            key="dobras_data_atual"
        )
    
    if data_anterior == data_atual:
        st.warning("Selecione datas diferentes para comparar.")
        return
    
    avaliacao_anterior = obter_avaliacao_por_data(cliente_id, data_anterior)
    avaliacao_atual = obter_avaliacao_por_data(cliente_id, data_atual)
    
    if not avaliacao_anterior or not avaliacao_atual:
        st.error("Erro ao carregar avaliações.")
        return
    
    dobras_anterior = avaliacao_anterior.get("dobras_cutaneas", {})
    dobras_atual = avaliacao_atual.get("dobras_cutaneas", {})
    
    # Verifica se há dados de dobras
    if not dobras_anterior or not dobras_atual:
        st.warning("Uma ou ambas as avaliações não possuem dados de dobras cutâneas.")
        return
    
    # Calcula resultados Pollock 7
    resultado_anterior = calcular_gordura_pollock7(dobras_anterior, idade, genero)
    resultado_atual = calcular_gordura_pollock7(dobras_atual, idade, genero)
    
    peso_anterior = avaliacao_anterior.get("peso_kg", 0)
    peso_atual = avaliacao_atual.get("peso_kg", 0)
    
    massas_anterior = calcular_massas_corporais(peso_anterior, resultado_anterior["percentual_gordura"])
    massas_atual = calcular_massas_corporais(peso_atual, resultado_atual["percentual_gordura"])
    
    # KPIs de Gordura Corporal
    st.markdown("#### 🔥 Evolução de Composição Corporal")
    
    col1, col2, col3, col4 = st.columns(4)
    
    perc_ant = resultado_anterior["percentual_gordura"]
    perc_atu = resultado_atual["percentual_gordura"]
    delta_perc = perc_atu - perc_ant
    
    with col1:
        st.metric(
            "% Gordura Anterior",
            f"{perc_ant:.1f}%",
            delta=None
        )
    
    with col2:
        st.metric(
            "% Gordura Atual",
            f"{perc_atu:.1f}%",
            delta=f"{delta_perc:+.1f}%",
            delta_color="inverse"
        )
    
    delta_gorda = massas_atual["massa_gorda"] - massas_anterior["massa_gorda"]
    delta_magra = massas_atual["massa_magra"] - massas_anterior["massa_magra"]
    
    with col3:
        st.metric(
            "Massa Gorda",
            f"{massas_atual['massa_gorda']:.1f} kg",
            delta=f"{delta_gorda:+.1f} kg",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "Massa Magra",
            f"{massas_atual['massa_magra']:.1f} kg",
            delta=f"{delta_magra:+.1f} kg",
            delta_color="normal"
        )
    
    st.divider()
    
    # Gráfico de barras comparativo de dobras
    st.markdown("#### 📊 Comparação por Ponto de Medição")
    
    nomes = []
    valores_anterior = []
    valores_atual = []
    
    for chave, nome in NOMES_DOBRAS.items():
        nomes.append(nome)
        valores_anterior.append(dobras_anterior.get(chave, 0))
        valores_atual.append(dobras_atual.get(chave, 0))
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=f'Anterior ({data_anterior})',
        x=nomes,
        y=valores_anterior,
        marker_color='#6c757d'
    ))
    
    fig.add_trace(go.Bar(
        name=f'Atual ({data_atual})',
        x=nomes,
        y=valores_atual,
        marker_color='#FF6B35'
    ))
    
    fig.update_layout(
        barmode='group',
        title="Dobras Cutâneas (mm)",
        xaxis_title="Ponto de Medição",
        yaxis_title="Espessura (mm)",
        template="plotly_dark",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada de variações
    st.markdown("#### 📋 Variação Detalhada")
    
    dados_tabela = []
    for chave, nome in NOMES_DOBRAS.items():
        anterior = dobras_anterior.get(chave, 0)
        atual = dobras_atual.get(chave, 0)
        diferenca = atual - anterior
        perc_var = ((atual - anterior) / anterior * 100) if anterior > 0 else 0
        
        dados_tabela.append({
            "Dobra": nome,
            "Anterior (mm)": anterior,
            "Atual (mm)": atual,
            "Variação (mm)": f"{diferenca:+.1f}",
            "Variação (%)": f"{perc_var:+.1f}%"
        })
    
    # Adiciona linha de soma total
    soma_ant = resultado_anterior["soma_dobras"]
    soma_atu = resultado_atual["soma_dobras"]
    dados_tabela.append({
        "Dobra": "**SOMA TOTAL**",
        "Anterior (mm)": soma_ant,
        "Atual (mm)": soma_atu,
        "Variação (mm)": f"{soma_atu - soma_ant:+.1f}",
        "Variação (%)": f"{((soma_atu - soma_ant) / soma_ant * 100) if soma_ant > 0 else 0:+.1f}%"
    })
    
    df = pd.DataFrame(dados_tabela)
    st.dataframe(df, use_container_width=True, hide_index=True)


def renderizar_evolucao_gordura(cliente_id: str, cliente: dict) -> None:
    """
    Renderiza gráfico de evolução do percentual de gordura.
    
    :param cliente_id: ID do cliente
    :param cliente: Dicionário com dados do cliente
    """
    st.markdown("### 📈 Evolução do % de Gordura")
    
    historico = obter_historico_avaliacoes(cliente_id)
    genero = cliente.get("genero", "Masculino")
    data_nascimento = cliente.get("data_nascimento", "")
    idade = calcular_idade(data_nascimento) if data_nascimento else 25
    
    datas = []
    percentuais = []
    massas_gordas = []
    massas_magras = []
    
    for avaliacao in historico:
        dobras = avaliacao.get("dobras_cutaneas", {})
        if dobras and any(v > 0 for v in dobras.values()):
            resultado = calcular_gordura_pollock7(dobras, idade, genero)
            peso = avaliacao.get("peso_kg", 0)
            massas = calcular_massas_corporais(peso, resultado["percentual_gordura"])
            
            datas.append(avaliacao.get("data", ""))
            percentuais.append(resultado["percentual_gordura"])
            massas_gordas.append(massas["massa_gorda"])
            massas_magras.append(massas["massa_magra"])
    
    if len(datas) < 2:
        st.info("Necessário pelo menos 2 avaliações com dobras cutâneas para visualizar evolução.")
        return
    
    # Gráfico de linha
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=datas,
        y=percentuais,
        mode='lines+markers',
        name='% Gordura',
        line=dict(color='#FF6B35', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title="Evolução do Percentual de Gordura Corporal",
        xaxis_title="Data",
        yaxis_title="% Gordura",
        template="plotly_dark",
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de massas
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=datas,
        y=massas_gordas,
        mode='lines+markers',
        name='Massa Gorda (kg)',
        line=dict(color='#e74c3c', width=2),
        fill='tozeroy',
        fillcolor='rgba(231, 76, 60, 0.2)'
    ))
    
    fig2.add_trace(go.Scatter(
        x=datas,
        y=massas_magras,
        mode='lines+markers',
        name='Massa Magra (kg)',
        line=dict(color='#2ecc71', width=2),
        fill='tozeroy',
        fillcolor='rgba(46, 204, 113, 0.2)'
    ))
    
    fig2.update_layout(
        title="Evolução das Massas Corporais",
        xaxis_title="Data",
        yaxis_title="Massa (kg)",
        template="plotly_dark",
        height=350
    )
    
    st.plotly_chart(fig2, use_container_width=True)


def renderizar_analise_simetria(cliente_id: str) -> None:
    """
    Renderiza a análise de simetria entre membros.
    
    :param cliente_id: ID do cliente
    """
    st.markdown("### ⚖️ Análise de Simetria")
    
    avaliacao = obter_ultima_avaliacao(cliente_id)
    
    if not avaliacao:
        st.info("Nenhuma avaliação disponível.")
        return
    
    perimetros = avaliacao.get("perimetros", {})
    analise = analisar_simetria_completa(perimetros)
    
    if not analise:
        st.info("Sem dados suficientes para análise de simetria.")
        return
    
    dados = []
    for item in analise:
        dados.append({
            "Membro": item["membro"],
            "Direito (cm)": item["valor_direito"],
            "Esquerdo (cm)": item["valor_esquerdo"],
            "Diferença (cm)": item["diferenca_cm"],
            "Diferença (%)": f"{item['diferenca_percentual']:.1f}%",
            "Dominante": item["lado_dominante"]
        })
    
    df = pd.DataFrame(dados)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Alerta se houver assimetria significativa (>5%)
    assimetrias = [a for a in analise if a["diferenca_percentual"] > 5]
    if assimetrias:
        st.warning(f"⚠️ {len(assimetrias)} ponto(s) com assimetria acima de 5%.")


def renderizar_pagina_historico() -> None:
    """
    Renderiza a página de histórico e evolução.
    """
    st.title("📈 Histórico e Evolução")
    
    # Verifica se há cliente selecionado
    if "cliente_selecionado_id" not in st.session_state or not st.session_state.cliente_selecionado_id:
        st.warning("⚠️ Selecione um cliente na barra lateral.")
        return
    
    cliente_id = st.session_state.cliente_selecionado_id
    cliente = buscar_cliente_por_id(cliente_id)
    
    if not cliente:
        st.error("Cliente não encontrado.")
        return
    
    st.info(f"📋 Histórico de: **{cliente.get('nome', 'Cliente')}**")
    
    historico = obter_historico_avaliacoes(cliente_id)
    
    if not historico:
        st.warning("Este cliente ainda não possui avaliações.")
        return
    
    # Abas para organizar
    aba_visao_geral, aba_comparacao, aba_dobras, aba_simetria = st.tabs([
        "📊 Visão Geral",
        "🔄 Comparação Perímetros",
        "📐 Dobras Cutâneas",
        "⚖️ Simetria"
    ])
    
    with aba_visao_geral:
        st.markdown("### 📋 Histórico de Avaliações")
        renderizar_tabela_historico(historico)
        
        st.divider()
        
        st.markdown("### 📈 Evolução do Peso")
        renderizar_grafico_evolucao_peso(historico)
        
        # Seletor de perímetro para ver evolução
        st.markdown("### 📐 Evolução de Perímetro")
        perimetro_selecionado = st.selectbox(
            "Selecione o perímetro",
            options=list(NOMES_PERIMETROS.keys()),
            format_func=lambda x: NOMES_PERIMETROS[x]
        )
        
        fig = criar_grafico_evolucao_perimetro(historico, perimetro_selecionado)
        st.plotly_chart(fig, use_container_width=True)
    
    with aba_comparacao:
        renderizar_comparacao_avaliacoes(cliente_id)
    
    with aba_dobras:
        # Evolução de gordura
        renderizar_evolucao_gordura(cliente_id, cliente)
        
        st.divider()
        
        # Comparação entre datas
        renderizar_comparacao_dobras(cliente_id, cliente)
    
    with aba_simetria:
        renderizar_analise_simetria(cliente_id)
