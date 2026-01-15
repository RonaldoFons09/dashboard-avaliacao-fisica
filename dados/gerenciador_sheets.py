"""
Gerenciador de Conexão com Google Sheets.

Este módulo centraliza a conexão com o Google Sheets usando gspread e
credenciais de service account.
"""

import json
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
def conectar_planilha() -> gspread.Spreadsheet:
    """
    Estabelece conexão com a planilha do Google Sheets.
    
    Usa credenciais de service account armazenadas em st.secrets ou
    arquivo local .streamlit/secrets.toml.
    
    :return: Objeto Spreadsheet do gspread
    """
    try:
        # Tenta carregar credenciais do Streamlit secrets
        credenciais_dict = st.secrets["gcp_service_account"]
        credenciais = Credentials.from_service_account_info(
            dict(credenciais_dict),
            scopes=ESCOPOS
        )
    except (KeyError, FileNotFoundError):
        # Fallback para arquivo local (desenvolvimento)
        try:
            from pathlib import Path
            caminho_credenciais = Path(__file__).parent.parent / ".streamlit" / "credentials.json"
            credenciais = Credentials.from_service_account_file(
                str(caminho_credenciais),
                scopes=ESCOPOS
            )
        except Exception as e:
            st.error(f"Erro ao carregar credenciais: {e}")
            st.info("Configure as credenciais no arquivo .streamlit/secrets.toml")
            return None
    
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_key(ID_PLANILHA)
    
    return planilha


def obter_aba_clientes() -> gspread.Worksheet:
    """
    Retorna a aba 'clientes' da planilha.
    
    :return: Objeto Worksheet do gspread
    """
    planilha = conectar_planilha()
    if planilha:
        return planilha.worksheet("clientes")
    return None


def obter_aba_avaliacoes() -> gspread.Worksheet:
    """
    Retorna a aba 'avaliacoes' da planilha.
    
    :return: Objeto Worksheet do gspread
    """
    planilha = conectar_planilha()
    if planilha:
        return planilha.worksheet("avaliacoes")
    return None


def verificar_conexao() -> bool:
    """
    Verifica se a conexão com o Google Sheets está funcionando.
    
    :return: True se conectado, False caso contrário
    """
    try:
        planilha = conectar_planilha()
        if planilha:
            # Tenta ler o título da planilha
            _ = planilha.title
            return True
    except Exception:
        pass
    return False
