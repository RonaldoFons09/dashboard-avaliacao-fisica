"""
Cartão de Perfil - Componente visual para exibir informações do cliente.

Este módulo contém funções para renderizar cards visuais com os dados
do cliente selecionado.
"""

import streamlit as st
from servicos.calculadora_corporal import calcular_idade


def renderizar_cartao_perfil(cliente: dict) -> None:
    """
    Renderiza um card visual com as informações básicas do cliente.
    
    :param cliente: Dicionário com dados do cliente
    """
    if not cliente:
        st.warning("Nenhum cliente selecionado.")
        return
    
    nome = cliente.get("nome", "Não informado")
    genero = cliente.get("genero", "Não informado")
    data_nascimento = cliente.get("data_nascimento", "")
    biotipo = cliente.get("biotipo", "Não informado")
    
    idade = calcular_idade(data_nascimento) if data_nascimento else "N/A"
    
    with st.container():
        st.markdown("""
        <style>
        .cartao-perfil {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px;
            color: white;
            margin-bottom: 20px;
        }
        .nome-cliente {
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .info-cliente {
            font-size: 1.1em;
            opacity: 0.9;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="cartao-perfil">
            <div class="nome-cliente">👤 {nome}</div>
            <div class="info-cliente">
                <p>🎂 {idade} anos | {genero}</p>
                <p>🏋️ Biotipo: {biotipo}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


def renderizar_cartao_perfil_compacto(cliente: dict) -> None:
    """
    Renderiza uma versão compacta do card de perfil para a sidebar.
    
    :param cliente: Dicionário com dados do cliente
    """
    if not cliente:
        return
    
    nome = cliente.get("nome", "Cliente")
    biotipo = cliente.get("biotipo", "")
    
    st.sidebar.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 15px;
        color: white;
        text-align: center;
        margin-bottom: 15px;
    ">
        <div style="font-size: 1.3em; font-weight: bold;">👤 {nome}</div>
        <div style="font-size: 0.9em; opacity: 0.8;">{biotipo}</div>
    </div>
    """, unsafe_allow_html=True)


def renderizar_resumo_avaliacao(avaliacao: dict) -> None:
    """
    Renderiza um resumo da última avaliação no card de perfil.
    
    :param avaliacao: Dicionário com dados da avaliação
    """
    if not avaliacao:
        st.info("Nenhuma avaliação registrada.")
        return
    
    data = avaliacao.get("data", "N/A")
    peso = avaliacao.get("peso_kg", 0)
    altura = avaliacao.get("altura_cm", 0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📅 Última avaliação", data)
    
    with col2:
        st.metric("⚖️ Peso", f"{peso} kg")
    
    with col3:
        st.metric("📏 Altura", f"{altura} cm")
