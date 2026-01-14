"""
Página Histórico - Visualização de evolução e comparações.

Esta página permite visualizar o histórico de avaliações do cliente,
gráficos de evolução e comparações entre diferentes datas.
"""

import streamlit as st
import pandas as pd
from dados.gerenciador_clientes import buscar_cliente_por_id
from dados.gerenciador_avaliacoes import (
    obter_historico_avaliacoes,
    listar_datas_avaliacoes,
    obter_avaliacao_por_data
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
from servicos.calculadora_corporal import calcular_imc


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


def renderizar_analise_simetria(cliente_id: str) -> None:
    """
    Renderiza a análise de simetria entre membros.
    
    :param cliente_id: ID do cliente
    """
    st.markdown("### ⚖️ Análise de Simetria")
    
    from dados.gerenciador_avaliacoes import obter_ultima_avaliacao
    
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
    aba_visao_geral, aba_comparacao, aba_simetria = st.tabs([
        "📊 Visão Geral",
        "🔄 Comparação",
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
    
    with aba_simetria:
        renderizar_analise_simetria(cliente_id)
