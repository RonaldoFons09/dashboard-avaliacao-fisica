"""
Gerenciador de Avaliações - Módulo de persistência de dados.

Este módulo é responsável por todas as operações relacionadas às avaliações
físicas dos clientes. Usa Google Sheets como banco de dados online.
"""

import json
import uuid
from datetime import datetime
from typing import Optional

import streamlit as st
from dados.gerenciador_sheets import obter_aba_avaliacoes


def criar_avaliacao_vazia() -> dict:
    """Cria uma estrutura de avaliação vazia com todos os campos."""
    return {
        "id": str(uuid.uuid4()),
        "data": datetime.now().strftime("%Y-%m-%d"),
        "peso_kg": 0.0,
        "altura_cm": 0.0,
        "nivel_atividade": "Sedentário",
        "perimetros": {
            "braco_direito_relaxado": 0.0,
            "braco_direito_contraido": 0.0,
            "braco_esquerdo_relaxado": 0.0,
            "braco_esquerdo_contraido": 0.0,
            "antebraco_direito": 0.0,
            "antebraco_esquerdo": 0.0,
            "ombro": 0.0,
            "torax": 0.0,
            "cintura": 0.0,
            "abdomen": 0.0,
            "quadril": 0.0,
            "coxa_superior_direita": 0.0,
            "coxa_superior_esquerda": 0.0,
            "coxa_media_direita": 0.0,
            "coxa_media_esquerda": 0.0,
            "coxa_inferior_direita": 0.0,
            "coxa_inferior_esquerda": 0.0,
            "panturrilha_direita": 0.0,
            "panturrilha_esquerda": 0.0
        },
        "dobras_cutaneas": {
            "peitoral": 0.0,
            "axilar_media": 0.0,
            "triceps": 0.0,
            "subescapular": 0.0,
            "abdominal": 0.0,
            "suprailiaca": 0.0,
            "coxa": 0.0
        }
    }


def adicionar_avaliacao(cliente_id: str, avaliacao: dict) -> bool:
    """Adiciona uma nova avaliação no Google Sheets."""
    if "id" not in avaliacao:
        avaliacao["id"] = str(uuid.uuid4())
    
    if "data" not in avaliacao:
        avaliacao["data"] = datetime.now().strftime("%Y-%m-%d")
    
    try:
        aba = obter_aba_avaliacoes()
        if not aba:
            return False
        
        # Serializa perímetros e dobras cutâneas como JSON
        perimetros_json = json.dumps(avaliacao.get("perimetros", {}), ensure_ascii=False)
        dobras_json = json.dumps(avaliacao.get("dobras_cutaneas", {}), ensure_ascii=False)
        
        linha = [
            avaliacao.get("id", str(uuid.uuid4())),
            cliente_id,
            avaliacao.get("data", ""),
            avaliacao.get("peso_kg", 0),
            avaliacao.get("altura_cm", 0),
            avaliacao.get("nivel_atividade", ""),
            perimetros_json,
            dobras_json
        ]
        
        aba.append_row(linha)
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar avaliação: {e}")
        return False


def obter_historico_avaliacoes(cliente_id: str) -> list[dict]:
    """Retorna todas as avaliações de um cliente ordenadas por data."""
    try:
        aba = obter_aba_avaliacoes()
        if not aba:
            return []
        
        registros = aba.get_all_records()
        avaliacoes = []
        
        for registro in registros:
            if str(registro.get("cliente_id", "")) == cliente_id:
                # Deserializa perímetros
                perimetros_json = registro.get("perimetros_json", "{}")
                if isinstance(perimetros_json, str):
                    try:
                        perimetros = json.loads(perimetros_json)
                    except json.JSONDecodeError:
                        perimetros = {}
                else:
                    perimetros = {}
                
                # Deserializa dobras cutâneas
                dobras_json = registro.get("dobras_cutaneas_json", "{}")
                if isinstance(dobras_json, str):
                    try:
                        dobras_cutaneas = json.loads(dobras_json)
                    except json.JSONDecodeError:
                        dobras_cutaneas = {}
                else:
                    dobras_cutaneas = {}
                
                avaliacao = {
                    "id": str(registro.get("id", "")),
                    "data": str(registro.get("data", "")),
                    "peso_kg": float(registro.get("peso_kg", 0) or 0),
                    "altura_cm": float(registro.get("altura_cm", 0) or 0),
                    "nivel_atividade": str(registro.get("nivel_atividade", "")),
                    "perimetros": perimetros,
                    "dobras_cutaneas": dobras_cutaneas
                }
                avaliacoes.append(avaliacao)
        
        return sorted(avaliacoes, key=lambda a: a.get("data", ""))
    except Exception as e:
        st.error(f"Erro ao carregar avaliações: {e}")
        return []


def obter_ultima_avaliacao(cliente_id: str) -> Optional[dict]:
    """Retorna a avaliação mais recente do cliente."""
    historico = obter_historico_avaliacoes(cliente_id)
    
    if not historico:
        return None
    
    return historico[-1]


def obter_primeira_avaliacao(cliente_id: str) -> Optional[dict]:
    """Retorna a primeira avaliação do cliente."""
    historico = obter_historico_avaliacoes(cliente_id)
    
    if not historico:
        return None
    
    return historico[0]


def obter_avaliacao_por_data(cliente_id: str, data: str) -> Optional[dict]:
    """Busca uma avaliação específica pela data."""
    historico = obter_historico_avaliacoes(cliente_id)
    
    for avaliacao in historico:
        if avaliacao.get("data") == data:
            return avaliacao
    
    return None


def contar_avaliacoes(cliente_id: str) -> int:
    """Retorna o número total de avaliações do cliente."""
    historico = obter_historico_avaliacoes(cliente_id)
    return len(historico)


def listar_datas_avaliacoes(cliente_id: str) -> list[str]:
    """Retorna lista de datas de todas as avaliações do cliente."""
    historico = obter_historico_avaliacoes(cliente_id)
    return [avaliacao.get("data", "") for avaliacao in historico]


def excluir_avaliacao(cliente_id: str, avaliacao_id: str) -> bool:
    """Remove uma avaliação específica do Google Sheets."""
    try:
        aba = obter_aba_avaliacoes()
        if not aba:
            return False
        
        celula = aba.find(avaliacao_id)
        if celula:
            aba.delete_rows(celula.row)
            return True
        return False
    except Exception as e:
        st.error(f"Erro ao excluir avaliação: {e}")
        return False
