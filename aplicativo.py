"""
Aplicativo de Avaliação Física - Ponto de entrada principal.

Este é o arquivo principal do dashboard Streamlit para gerenciamento
de avaliações físicas de múltiplos clientes.

Para executar:
    streamlit run aplicativo.py
"""

import streamlit as st
from dados.gerenciador_clientes import listar_nomes_clientes, buscar_cliente_por_nome
from paginas.pagina_dashboard import renderizar_pagina_dashboard
from paginas.pagina_clientes import renderizar_pagina_clientes
from paginas.pagina_avaliacao import renderizar_pagina_avaliacao
from paginas.pagina_historico import renderizar_pagina_historico
from paginas.pagina_relatorios import renderizar_pagina_relatorios


# Configuração da página
st.set_page_config(
    page_title="Avaliação Física",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para tema escuro moderno
st.markdown("""
<style>
    /* Tema geral */
    .stApp {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    }
    
    /* Cards e containers */
    .stMetric {
        background-color: #1e1e2d;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Forms */
    .stForm {
        background-color: #1e1e2d;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #2a2a3a;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e2d;
        border-radius: 8px;
        padding: 10px 20px;
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background-color: #1e1e2d;
        border-color: #2a2a3a;
        color: white;
    }
    
    /* Divider */
    hr {
        border-color: #2a2a3a;
    }
    
    /* Info/Warning boxes */
    .stAlert {
        background-color: #1e1e2d;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


def configurar_sidebar() -> str:
    """
    Configura a barra lateral com seleção de cliente e navegação.
    
    :return: Página selecionada
    """
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #667eea; margin: 0;">🏋️</h1>
        <h3 style="color: white; margin: 5px 0;">Avaliação Física</h3>
        <p style="color: #888; font-size: 0.9em;">Sistema de Gestão</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.divider()
    
    # Seleção de cliente
    st.sidebar.markdown("### 👤 Cliente Ativo")
    
    nomes = listar_nomes_clientes()
    
    if nomes:
        # Encontra o índice do cliente selecionado
        indice_atual = 0
        if "cliente_selecionado_id" in st.session_state and st.session_state.cliente_selecionado_id:
            from dados.gerenciador_clientes import buscar_cliente_por_id
            cliente_atual = buscar_cliente_por_id(st.session_state.cliente_selecionado_id)
            if cliente_atual and cliente_atual.get("nome") in nomes:
                indice_atual = nomes.index(cliente_atual.get("nome"))
        
        nome_selecionado = st.sidebar.selectbox(
            "Selecione o cliente",
            options=nomes,
            index=indice_atual,
            label_visibility="collapsed"
        )
        
        # Atualiza o cliente selecionado
        cliente = buscar_cliente_por_nome(nome_selecionado)
        if cliente:
            st.session_state.cliente_selecionado_id = cliente.get("id")
    else:
        st.sidebar.info("Nenhum cliente cadastrado")
        st.session_state.cliente_selecionado_id = None
    
    st.sidebar.divider()
    
    # Navegação
    st.sidebar.markdown("### 📍 Navegação")
    
    pagina = st.sidebar.radio(
        "Menu",
        options=[
            "📊 Dashboard",
            "👥 Clientes",
            "📝 Nova Avaliação",
            "📈 Histórico",
            "📄 Relatórios"
        ],
        label_visibility="collapsed"
    )
    
    st.sidebar.divider()
    
    # Rodapé
    st.sidebar.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8em; padding: 20px 0;">
        Desenvolvido com ❤️<br>
        Streamlit + Python
    </div>
    """, unsafe_allow_html=True)
    
    return pagina


def main() -> None:
    """
    Função principal que orquestra a aplicação.
    """
    # Inicializa session state
    if "cliente_selecionado_id" not in st.session_state:
        st.session_state.cliente_selecionado_id = None
    
    # Configura sidebar e obtém página selecionada
    pagina = configurar_sidebar()
    
    # Renderiza a página selecionada
    if pagina == "📊 Dashboard":
        renderizar_pagina_dashboard()
    elif pagina == "👥 Clientes":
        renderizar_pagina_clientes()
    elif pagina == "📝 Nova Avaliação":
        renderizar_pagina_avaliacao()
    elif pagina == "📈 Histórico":
        renderizar_pagina_historico()
    elif pagina == "📄 Relatórios":
        renderizar_pagina_relatorios()


if __name__ == "__main__":
    main()
