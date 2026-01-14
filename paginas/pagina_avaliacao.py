"""
Página Avaliação - Registro de nova avaliação física.

Esta página permite registrar uma nova avaliação completa do cliente,
incluindo peso, altura, nível de atividade e todos os perímetros corporais.
"""

import streamlit as st
from datetime import date
from dados.gerenciador_clientes import buscar_cliente_por_id
from dados.gerenciador_avaliacoes import adicionar_avaliacao, criar_avaliacao_vazia
from servicos.calculadora_corporal import (
    calcular_imc,
    classificar_imc,
    calcular_tmb,
    calcular_gasto_calorico_diario,
    calcular_idade,
    listar_niveis_atividade
)


def renderizar_formulario_avaliacao(cliente: dict) -> None:
    """
    Renderiza o formulário completo de avaliação.
    
    :param cliente: Dicionário com dados do cliente
    """
    genero = cliente.get("genero", "Masculino")
    data_nascimento = cliente.get("data_nascimento", "")
    idade = calcular_idade(data_nascimento) if data_nascimento else 25
    
    with st.form("form_avaliacao"):
        st.markdown("### 📋 Dados Gerais")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            data_avaliacao = st.date_input(
                "Data da Avaliação",
                value=date.today(),
                max_value=date.today()
            )
        
        with col2:
            peso_kg = st.number_input(
                "Peso (kg)",
                min_value=20.0,
                max_value=300.0,
                value=70.0,
                step=0.1
            )
        
        with col3:
            altura_cm = st.number_input(
                "Altura (cm)",
                min_value=100.0,
                max_value=250.0,
                value=170.0,
                step=0.5
            )
        
        with col4:
            nivel_atividade = st.selectbox(
                "Nível de Atividade",
                options=listar_niveis_atividade()
            )
        
        # Preview de cálculos em tempo real
        imc = calcular_imc(peso_kg, altura_cm)
        classificacao = classificar_imc(imc)
        tmb = calcular_tmb(peso_kg, altura_cm, idade, genero)
        gasto = calcular_gasto_calorico_diario(tmb, nivel_atividade)
        
        st.info(f"📊 IMC: **{imc}** ({classificacao}) | 🔥 TMB: **{tmb:.0f}** kcal | ⚡ Gasto Diário: **{gasto:.0f}** kcal")
        
        st.divider()
        st.markdown("### 📏 Perímetros Corporais (cm)")
        
        # Abas para organizar os perímetros
        aba_superior, aba_tronco, aba_inferior = st.tabs([
            "💪 Membros Superiores",
            "🧍 Tronco",
            "🦵 Membros Inferiores"
        ])
        
        with aba_superior:
            st.markdown("**Braço**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                braco_dir_rel = st.number_input("Dir. Relaxado", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="braco_dir_rel")
            with col2:
                braco_dir_con = st.number_input("Dir. Contraído", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="braco_dir_con")
            with col3:
                braco_esq_rel = st.number_input("Esq. Relaxado", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="braco_esq_rel")
            with col4:
                braco_esq_con = st.number_input("Esq. Contraído", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="braco_esq_con")
            
            st.markdown("**Antebraço**")
            col1, col2 = st.columns(2)
            
            with col1:
                antebraco_dir = st.number_input("Direito", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="antebraco_dir")
            with col2:
                antebraco_esq = st.number_input("Esquerdo", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="antebraco_esq")
        
        with aba_tronco:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                ombro = st.number_input("Ombro", min_value=0.0, max_value=200.0, value=0.0, step=0.5, key="ombro")
                cintura = st.number_input("Cintura", min_value=0.0, max_value=200.0, value=0.0, step=0.5, key="cintura")
            
            with col2:
                torax = st.number_input("Tórax", min_value=0.0, max_value=200.0, value=0.0, step=0.5, key="torax")
                abdomen = st.number_input("Abdômen", min_value=0.0, max_value=200.0, value=0.0, step=0.5, key="abdomen")
            
            with col3:
                quadril = st.number_input("Quadril", min_value=0.0, max_value=200.0, value=0.0, step=0.5, key="quadril")
        
        with aba_inferior:
            st.markdown("**Coxa Superior**")
            col1, col2 = st.columns(2)
            with col1:
                coxa_sup_dir = st.number_input("Direita", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="coxa_sup_dir")
            with col2:
                coxa_sup_esq = st.number_input("Esquerda", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="coxa_sup_esq")
            
            st.markdown("**Coxa Média**")
            col1, col2 = st.columns(2)
            with col1:
                coxa_med_dir = st.number_input("Direita", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="coxa_med_dir")
            with col2:
                coxa_med_esq = st.number_input("Esquerda", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="coxa_med_esq")
            
            st.markdown("**Coxa Inferior**")
            col1, col2 = st.columns(2)
            with col1:
                coxa_inf_dir = st.number_input("Direita", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="coxa_inf_dir")
            with col2:
                coxa_inf_esq = st.number_input("Esquerda", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="coxa_inf_esq")
            
            st.markdown("**Panturrilha**")
            col1, col2 = st.columns(2)
            with col1:
                panturrilha_dir = st.number_input("Direita", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="panturrilha_dir")
            with col2:
                panturrilha_esq = st.number_input("Esquerda", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="panturrilha_esq")
        
        st.divider()
        
        submitted = st.form_submit_button("💾 Salvar Avaliação", use_container_width=True, type="primary")
        
        if submitted:
            if peso_kg <= 0 or altura_cm <= 0:
                st.error("❌ Peso e altura são obrigatórios.")
            else:
                avaliacao = {
                    "data": data_avaliacao.strftime("%Y-%m-%d"),
                    "peso_kg": peso_kg,
                    "altura_cm": altura_cm,
                    "nivel_atividade": nivel_atividade,
                    "perimetros": {
                        "braco_direito_relaxado": braco_dir_rel,
                        "braco_direito_contraido": braco_dir_con,
                        "braco_esquerdo_relaxado": braco_esq_rel,
                        "braco_esquerdo_contraido": braco_esq_con,
                        "antebraco_direito": antebraco_dir,
                        "antebraco_esquerdo": antebraco_esq,
                        "ombro": ombro,
                        "torax": torax,
                        "cintura": cintura,
                        "abdomen": abdomen,
                        "quadril": quadril,
                        "coxa_superior_direita": coxa_sup_dir,
                        "coxa_superior_esquerda": coxa_sup_esq,
                        "coxa_media_direita": coxa_med_dir,
                        "coxa_media_esquerda": coxa_med_esq,
                        "coxa_inferior_direita": coxa_inf_dir,
                        "coxa_inferior_esquerda": coxa_inf_esq,
                        "panturrilha_direita": panturrilha_dir,
                        "panturrilha_esquerda": panturrilha_esq
                    }
                }
                
                cliente_id = st.session_state.cliente_selecionado_id
                
                if adicionar_avaliacao(cliente_id, avaliacao):
                    st.success("✅ Avaliação salva com sucesso!")
                    st.balloons()
                else:
                    st.error("❌ Erro ao salvar avaliação.")


def renderizar_pagina_avaliacao() -> None:
    """
    Renderiza a página de nova avaliação.
    """
    st.title("📝 Nova Avaliação")
    
    # Verifica se há cliente selecionado
    if "cliente_selecionado_id" not in st.session_state or not st.session_state.cliente_selecionado_id:
        st.warning("⚠️ Selecione um cliente na barra lateral antes de registrar uma avaliação.")
        return
    
    cliente_id = st.session_state.cliente_selecionado_id
    cliente = buscar_cliente_por_id(cliente_id)
    
    if not cliente:
        st.error("Cliente não encontrado.")
        return
    
    st.info(f"📋 Registrando avaliação para: **{cliente.get('nome', 'Cliente')}**")
    
    renderizar_formulario_avaliacao(cliente)
