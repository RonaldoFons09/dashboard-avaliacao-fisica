"""
Gerenciador de Conexão com Google Sheets.

Este módulo centraliza a conexão com o Google Sheets usando gspread e
credenciais de service account armazenadas no st.secrets.
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


# ID da planilha do Google Sheets (extraído da URL)
ID_PLANILHA = "1_5TORA8YU0pgIThaTMiQwGJAChCnodrFeJLRLxuC0YU"

# Escopos necessários para acessar Google Sheets e Drive
ESCOPOS = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


@st.cache_resource
def conectar_planilha():
    """
    Estabelece conexão com a planilha do Google Sheets.
    Usa credenciais de st.secrets["gcp_service_account"].
    """
    try:
        # Carrega credenciais do Streamlit secrets
        credenciais_dict = dict(st.secrets["gcp_service_account"])
        credenciais = Credentials.from_service_account_info(
            credenciais_dict,
            scopes=ESCOPOS
        )
        
        cliente = gspread.authorize(credenciais)
        planilha = cliente.open_by_key(ID_PLANILHA)
        return planilha
        
    except Exception as e:
        st.error(f"Erro ao conectar com Google Sheets: {e}")
        return None


def obter_aba_clientes():
    """Retorna a aba 'clientes' da planilha."""
    planilha = conectar_planilha()
    if planilha:
        try:
            return planilha.worksheet("clientes")
        except Exception as e:
            st.error(f"Erro ao acessar aba 'clientes': {e}")
    return None


def obter_aba_avaliacoes():
    """Retorna a aba 'avaliacoes' da planilha."""
    planilha = conectar_planilha()
    if planilha:
        try:
            return planilha.worksheet("avaliacoes")
        except Exception as e:
            st.error(f"Erro ao acessar aba 'avaliacoes': {e}")
    return None


def verificar_conexao() -> bool:
    """Verifica se a conexão com o Google Sheets está funcionando."""
    planilha = conectar_planilha()
    return planilha is not None
