"""
Página Dashboard - Visão geral do cliente com KPIs e gráficos.

Esta página exibe um resumo completo do cliente selecionado,
incluindo métricas principais e visualizações.
"""

import streamlit as st
from dados.gerenciador_clientes import buscar_cliente_por_id
from dados.gerenciador_avaliacoes import obter_ultima_avaliacao, obter_historico_avaliacoes
from componentes.cartao_perfil import renderizar_cartao_perfil, renderizar_resumo_avaliacao
from componentes.indicadores_kpi import renderizar_kpis_principais, renderizar_kpi_imc_detalhado
from componentes.grafico_radar import renderizar_grafico_radar
from componentes.grafico_evolucao import renderizar_grafico_evolucao_peso
from servicos.calculadora_corporal import (
    calcular_imc,
    classificar_imc,
    calcular_tmb,
    calcular_gasto_calorico_diario,
    calcular_idade,
    calcular_peso_ideal
)
from servicos.analisador_perimetros import calcular_relacao_cintura_quadril, classificar_rcq


def renderizar_pagina_dashboard() -> None:
    """
    Renderiza a página principal do dashboard.
    """
    st.title("📊 Dashboard")
    
    # Verifica se há cliente selecionado
    if "cliente_selecionado_id" not in st.session_state or not st.session_state.cliente_selecionado_id:
        st.info("👈 Selecione um cliente na barra lateral para visualizar o dashboard.")
        st.markdown("""
        ### Bem-vindo ao Sistema de Avaliação Física!
        
        Para começar:
        1. **Cadastre um cliente** na página "Clientes"
        2. **Selecione o cliente** na barra lateral
        3. **Registre uma avaliação** na página "Nova Avaliação"
        4. **Visualize os resultados** aqui no Dashboard
        """)
        return
    
    # Carrega dados do cliente
    cliente_id = st.session_state.cliente_selecionado_id
    cliente = buscar_cliente_por_id(cliente_id)
    
    if not cliente:
        st.error("Cliente não encontrado.")
        return
    
    # Carrega última avaliação
    ultima_avaliacao = obter_ultima_avaliacao(cliente_id)
    
    # Seção: Perfil do Cliente
    renderizar_cartao_perfil(cliente)
    
    if not ultima_avaliacao:
        st.warning("⚠️ Este cliente ainda não possui avaliações registradas.")
        st.info("Vá para a página 'Nova Avaliação' para registrar a primeira avaliação.")
        return
    
    # Seção: KPIs Principais
    st.markdown("### 📈 Indicadores Principais")
    renderizar_kpis_principais(cliente, ultima_avaliacao)
    
    st.divider()
    
    # Layout em duas colunas
    col_esquerda, col_direita = st.columns([1, 1])
    
    with col_esquerda:
        # Seção: Análise Detalhada
        st.markdown("### 🎯 Análise Detalhada")
        
        peso = ultima_avaliacao.get("peso_kg", 0)
        altura = ultima_avaliacao.get("altura_cm", 0)
        genero = cliente.get("genero", "Masculino")
        data_nascimento = cliente.get("data_nascimento", "")
        idade = calcular_idade(data_nascimento) if data_nascimento else 25
        nivel_atividade = ultima_avaliacao.get("nivel_atividade", "Sedentário")
        perimetros = ultima_avaliacao.get("perimetros", {})
        
        # IMC Detalhado
        imc = calcular_imc(peso, altura)
        classificacao = classificar_imc(imc)
        peso_min, peso_max = calcular_peso_ideal(altura, genero)
        
        st.markdown(f"""
        **IMC:** {imc} ({classificacao})  
        **Faixa de peso ideal:** {peso_min} - {peso_max} kg
        """)
        
        # TMB e Gasto
        tmb = calcular_tmb(peso, altura, idade, genero)
        gasto = calcular_gasto_calorico_diario(tmb, nivel_atividade)
        
        st.markdown(f"""
        **Taxa Metabólica Basal:** {tmb:.0f} kcal/dia  
        **Gasto Total ({nivel_atividade}):** {gasto:.0f} kcal/dia
        """)
        
        # RCQ
        rcq = calcular_relacao_cintura_quadril(perimetros)
        if rcq:
            classificacao_rcq = classificar_rcq(rcq, genero)
            st.markdown(f"""
            **Relação Cintura-Quadril:** {rcq} ({classificacao_rcq})
            """)
    
    with col_direita:
        # Seção: Gráfico Radar
        st.markdown("### 📐 Perímetros Corporais")
        perimetros = ultima_avaliacao.get("perimetros", {})
        renderizar_grafico_radar(perimetros)
    
    st.divider()
    
    # Seção: Evolução (se houver mais de uma avaliação)
    historico = obter_historico_avaliacoes(cliente_id)
    
    if len(historico) > 1:
        st.markdown("### 📈 Evolução do Peso")
        renderizar_grafico_evolucao_peso(historico)
    else:
        st.info("💡 Registre mais avaliações para visualizar gráficos de evolução.")
