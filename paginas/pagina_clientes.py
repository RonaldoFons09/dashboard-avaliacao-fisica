"""
Página Clientes - Cadastro e gestão de clientes.

Esta página permite cadastrar novos clientes, visualizar a lista
de clientes existentes e editar informações básicas.
"""

import streamlit as st
from datetime import date
from dados.gerenciador_clientes import (
    carregar_todos_clientes,
    criar_novo_cliente,
    buscar_cliente_por_nome,
    excluir_cliente,
    contar_clientes
)
from servicos.calculadora_corporal import calcular_idade


# Opções para os selectboxes
OPCOES_GENERO = ["Masculino", "Feminino"]
OPCOES_BIOTIPO = ["Ectomorfo", "Mesomorfo", "Endomorfo"]


def renderizar_formulario_novo_cliente() -> None:
    """
    Renderiza o formulário de cadastro de novo cliente.
    """
    st.markdown("### ➕ Cadastrar Novo Cliente")
    
    with st.form("form_novo_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input(
                "Nome completo *",
                placeholder="Ex: João da Silva"
            )
            
            genero = st.selectbox(
                "Gênero *",
                options=OPCOES_GENERO
            )
        
        with col2:
            data_nascimento = st.date_input(
                "Data de nascimento *",
                value=date(2000, 1, 1),
                min_value=date(1920, 1, 1),
                max_value=date.today()
            )
            
            biotipo = st.selectbox(
                "Biotipo",
                options=OPCOES_BIOTIPO,
                help="Ectomorfo: magro | Mesomorfo: atlético | Endomorfo: robusto"
            )
        
        submitted = st.form_submit_button("💾 Cadastrar Cliente", use_container_width=True)
        
        if submitted:
            if not nome or not nome.strip():
                st.error("❌ O nome é obrigatório.")
            elif buscar_cliente_por_nome(nome.strip()):
                st.error("❌ Já existe um cliente com este nome.")
            else:
                cliente = criar_novo_cliente(
                    nome=nome.strip(),
                    genero=genero,
                    data_nascimento=data_nascimento.strftime("%Y-%m-%d"),
                    biotipo=biotipo
                )
                st.success(f"✅ Cliente '{nome}' cadastrado com sucesso!")
                st.balloons()
                
                # Seleciona automaticamente o novo cliente
                st.session_state.cliente_selecionado_id = cliente["id"]
                st.rerun()


def renderizar_lista_clientes() -> None:
    """
    Renderiza a lista de clientes cadastrados.
    """
    st.markdown("### 👥 Clientes Cadastrados")
    
    clientes = carregar_todos_clientes()
    
    if not clientes:
        st.info("Nenhum cliente cadastrado ainda.")
        return
    
    st.markdown(f"**Total:** {len(clientes)} cliente(s)")
    
    for cliente in clientes:
        cliente_id = cliente.get("id", "")
        nome = cliente.get("nome", "Sem nome")
        genero = cliente.get("genero", "")
        biotipo = cliente.get("biotipo", "")
        data_nascimento = cliente.get("data_nascimento", "")
        idade = calcular_idade(data_nascimento) if data_nascimento else "N/A"
        qtd_avaliacoes = len(cliente.get("avaliacoes", []))
        
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"""
                **{nome}**  
                {idade} anos • {genero} • {biotipo}  
                📋 {qtd_avaliacoes} avaliação(ões)
                """)
            
            with col2:
                if st.button("📊 Selecionar", key=f"sel_{cliente_id}"):
                    st.session_state.cliente_selecionado_id = cliente_id
                    st.success(f"Cliente '{nome}' selecionado!")
                    st.rerun()
            
            with col3:
                if st.button("🗑️", key=f"del_{cliente_id}", help="Excluir cliente"):
                    if excluir_cliente(cliente_id):
                        st.warning(f"Cliente '{nome}' excluído.")
                        if st.session_state.get("cliente_selecionado_id") == cliente_id:
                            st.session_state.cliente_selecionado_id = None
                        st.rerun()
            
            st.divider()


def renderizar_pagina_clientes() -> None:
    """
    Renderiza a página completa de gestão de clientes.
    """
    st.title("👥 Clientes")
    
    # Abas para organizar a página
    aba_cadastro, aba_lista = st.tabs(["➕ Novo Cliente", "📋 Lista de Clientes"])
    
    with aba_cadastro:
        renderizar_formulario_novo_cliente()
    
    with aba_lista:
        renderizar_lista_clientes()
