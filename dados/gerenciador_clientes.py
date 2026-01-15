"""
Gerenciador de Clientes - Módulo de persistência de dados.

Este módulo é responsável por todas as operações de CRUD relacionadas
aos clientes. Usa Google Sheets como banco de dados online.
"""

import json
import uuid
from typing import Optional

import streamlit as st
from dados.gerenciador_sheets import obter_aba_clientes


def carregar_todos_clientes() -> list[dict]:
    """Carrega todos os clientes do Google Sheets."""
    try:
        aba = obter_aba_clientes()
        if not aba:
            return []
        
        registros = aba.get_all_records()
        clientes = []
        
        for registro in registros:
            if registro.get("id"):
                cliente = {
                    "id": str(registro.get("id", "")),
                    "nome": str(registro.get("nome", "")),
                    "genero": str(registro.get("genero", "")),
                    "data_nascimento": str(registro.get("data_nascimento", "")),
                    "biotipo": str(registro.get("biotipo", "")),
                    "avaliacoes": []  # Avaliações são carregadas do gerenciador_avaliacoes
                }
                clientes.append(cliente)
        
        return clientes
    except Exception as e:
        st.error(f"Erro ao carregar clientes: {e}")
        return []


def buscar_cliente_por_id(cliente_id: str) -> Optional[dict]:
    """Busca um cliente específico pelo seu ID único."""
    clientes = carregar_todos_clientes()
    
    for cliente in clientes:
        if cliente.get("id") == cliente_id:
            return cliente
    
    return None


def buscar_cliente_por_nome(nome: str) -> Optional[dict]:
    """Busca um cliente pelo nome exato."""
    clientes = carregar_todos_clientes()
    
    for cliente in clientes:
        if cliente.get("nome") == nome:
            return cliente
    
    return None


def listar_nomes_clientes() -> list[str]:
    """Retorna lista com os nomes de todos os clientes."""
    clientes = carregar_todos_clientes()
    nomes = [cliente.get("nome", "") for cliente in clientes]
    return sorted(nomes)


def criar_novo_cliente(
    nome: str,
    genero: str,
    data_nascimento: str,
    biotipo: str
) -> dict:
    """Cria um novo cliente com ID único no Google Sheets."""
    novo_cliente = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "genero": genero,
        "data_nascimento": data_nascimento,
        "biotipo": biotipo,
        "avaliacoes": []
    }
    
    try:
        aba = obter_aba_clientes()
        if aba:
            linha = [
                novo_cliente["id"],
                novo_cliente["nome"],
                novo_cliente["genero"],
                novo_cliente["data_nascimento"],
                novo_cliente["biotipo"]
            ]
            aba.append_row(linha)
    except Exception as e:
        st.error(f"Erro ao criar cliente: {e}")
    
    return novo_cliente


def atualizar_cliente(cliente_id: str, dados_atualizados: dict) -> bool:
    """Atualiza os dados de um cliente existente."""
    try:
        aba = obter_aba_clientes()
        if not aba:
            return False
        
        # Encontra a linha do cliente
        celula = aba.find(cliente_id)
        if not celula:
            return False
        
        linha = celula.row
        
        # Atualiza os campos
        if "nome" in dados_atualizados:
            aba.update_cell(linha, 2, dados_atualizados["nome"])
        if "genero" in dados_atualizados:
            aba.update_cell(linha, 3, dados_atualizados["genero"])
        if "data_nascimento" in dados_atualizados:
            aba.update_cell(linha, 4, dados_atualizados["data_nascimento"])
        if "biotipo" in dados_atualizados:
            aba.update_cell(linha, 5, dados_atualizados["biotipo"])
        
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar cliente: {e}")
        return False


def excluir_cliente(cliente_id: str) -> bool:
    """Remove um cliente do Google Sheets."""
    try:
        aba = obter_aba_clientes()
        if not aba:
            return False
        
        celula = aba.find(cliente_id)
        if celula:
            aba.delete_rows(celula.row)
            return True
        return False
    except Exception as e:
        st.error(f"Erro ao excluir cliente: {e}")
        return False


def contar_clientes() -> int:
    """Retorna a quantidade total de clientes cadastrados."""
    clientes = carregar_todos_clientes()
    return len(clientes)
