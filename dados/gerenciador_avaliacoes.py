"""
Gerenciador de Avaliações - Módulo de persistência de dados.

Este módulo é responsável por todas as operações relacionadas às avaliações
físicas dos clientes, incluindo adicionar, consultar e comparar avaliações.

Usa Google Sheets como banco de dados quando disponível, com fallback para JSON local.
"""

import json
import uuid
from datetime import datetime
from typing import Optional

# Tenta importar o gerenciador de Sheets
try:
    from dados.gerenciador_sheets import obter_aba_avaliacoes, verificar_conexao
    SHEETS_DISPONIVEL = True
except ImportError:
    SHEETS_DISPONIVEL = False

from dados.gerenciador_clientes import (
    buscar_cliente_por_id,
    _carregar_dados_json,
    _salvar_dados_json,
    _usar_sheets
)


def criar_avaliacao_vazia() -> dict:
    """
    Cria uma estrutura de avaliação vazia com todos os campos.
    
    :return: Dicionário com estrutura padrão de avaliação
    """
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
        }
    }


def _carregar_avaliacoes_sheets(cliente_id: str) -> list[dict]:
    """Carrega avaliações de um cliente do Google Sheets."""
    try:
        aba = obter_aba_avaliacoes()
        if not aba:
            return []
        
        registros = aba.get_all_records()
        avaliacoes = []
        
        for registro in registros:
            if str(registro.get("cliente_id", "")) == cliente_id:
                perimetros_json = registro.get("perimetros_json", "{}")
                if isinstance(perimetros_json, str):
                    try:
                        perimetros = json.loads(perimetros_json)
                    except json.JSONDecodeError:
                        perimetros = {}
                else:
                    perimetros = {}
                
                avaliacao = {
                    "id": str(registro.get("id", "")),
                    "data": str(registro.get("data", "")),
                    "peso_kg": float(registro.get("peso_kg", 0)),
                    "altura_cm": float(registro.get("altura_cm", 0)),
                    "nivel_atividade": str(registro.get("nivel_atividade", "")),
                    "perimetros": perimetros
                }
                avaliacoes.append(avaliacao)
        
        return avaliacoes
    except Exception as e:
        print(f"Erro ao carregar avaliações do Sheets: {e}")
        return []


def _adicionar_avaliacao_sheets(cliente_id: str, avaliacao: dict) -> bool:
    """Adiciona uma avaliação no Google Sheets."""
    try:
        aba = obter_aba_avaliacoes()
        if not aba:
            return False
        
        perimetros_json = json.dumps(avaliacao.get("perimetros", {}), ensure_ascii=False)
        
        linha = [
            avaliacao.get("id", str(uuid.uuid4())),
            cliente_id,
            avaliacao.get("data", ""),
            avaliacao.get("peso_kg", 0),
            avaliacao.get("altura_cm", 0),
            avaliacao.get("nivel_atividade", ""),
            perimetros_json
        ]
        
        aba.append_row(linha)
        return True
    except Exception as e:
        print(f"Erro ao adicionar avaliação no Sheets: {e}")
        return False


def adicionar_avaliacao(cliente_id: str, avaliacao: dict) -> bool:
    """
    Adiciona uma nova avaliação ao histórico do cliente.
    
    :param cliente_id: ID único do cliente
    :param avaliacao: Dicionário com dados da avaliação
    :return: True se adicionado com sucesso, False se cliente não encontrado
    """
    # Garante que a avaliação tenha um ID único
    if "id" not in avaliacao:
        avaliacao["id"] = str(uuid.uuid4())
    
    # Garante que tenha data
    if "data" not in avaliacao:
        avaliacao["data"] = datetime.now().strftime("%Y-%m-%d")
    
    if _usar_sheets():
        return _adicionar_avaliacao_sheets(cliente_id, avaliacao)
    
    # Fallback para JSON
    clientes = _carregar_dados_json()
    
    for cliente in clientes:
        if cliente.get("id") == cliente_id:
            cliente["avaliacoes"].append(avaliacao)
            _salvar_dados_json(clientes)
            return True
    
    return False


def obter_historico_avaliacoes(cliente_id: str) -> list[dict]:
    """
    Retorna todas as avaliações de um cliente ordenadas por data.
    
    :param cliente_id: ID único do cliente
    :return: Lista de avaliações ordenadas da mais antiga para mais recente
    """
    if _usar_sheets():
        avaliacoes = _carregar_avaliacoes_sheets(cliente_id)
        return sorted(avaliacoes, key=lambda a: a.get("data", ""))
    
    # Fallback para JSON
    cliente = buscar_cliente_por_id(cliente_id)
    
    if not cliente:
        return []
    
    avaliacoes = cliente.get("avaliacoes", [])
    return sorted(avaliacoes, key=lambda a: a.get("data", ""))


def obter_ultima_avaliacao(cliente_id: str) -> Optional[dict]:
    """
    Retorna a avaliação mais recente do cliente.
    
    :param cliente_id: ID único do cliente
    :return: Dicionário da última avaliação ou None se não houver avaliações
    """
    historico = obter_historico_avaliacoes(cliente_id)
    
    if not historico:
        return None
    
    return historico[-1]


def obter_primeira_avaliacao(cliente_id: str) -> Optional[dict]:
    """
    Retorna a primeira avaliação do cliente (avaliação inicial).
    
    :param cliente_id: ID único do cliente
    :return: Dicionário da primeira avaliação ou None se não houver avaliações
    """
    historico = obter_historico_avaliacoes(cliente_id)
    
    if not historico:
        return None
    
    return historico[0]


def obter_avaliacao_por_data(cliente_id: str, data: str) -> Optional[dict]:
    """
    Busca uma avaliação específica pela data.
    
    :param cliente_id: ID único do cliente
    :param data: Data no formato YYYY-MM-DD
    :return: Dicionário da avaliação ou None se não encontrada
    """
    historico = obter_historico_avaliacoes(cliente_id)
    
    for avaliacao in historico:
        if avaliacao.get("data") == data:
            return avaliacao
    
    return None


def contar_avaliacoes(cliente_id: str) -> int:
    """
    Retorna o número total de avaliações do cliente.
    
    :param cliente_id: ID único do cliente
    :return: Quantidade de avaliações
    """
    historico = obter_historico_avaliacoes(cliente_id)
    return len(historico)


def listar_datas_avaliacoes(cliente_id: str) -> list[str]:
    """
    Retorna lista de datas de todas as avaliações do cliente.
    
    :param cliente_id: ID único do cliente
    :return: Lista de datas no formato YYYY-MM-DD
    """
    historico = obter_historico_avaliacoes(cliente_id)
    return [avaliacao.get("data", "") for avaliacao in historico]


def excluir_avaliacao(cliente_id: str, avaliacao_id: str) -> bool:
    """
    Remove uma avaliação específica do histórico do cliente.
    
    :param cliente_id: ID único do cliente
    :param avaliacao_id: ID único da avaliação
    :return: True se excluído com sucesso, False caso contrário
    """
    # Para Sheets, seria necessário encontrar e deletar a linha
    # Por ora, mantemos apenas JSON
    clientes = _carregar_dados_json()
    
    for cliente in clientes:
        if cliente.get("id") == cliente_id:
            avaliacoes = cliente.get("avaliacoes", [])
            quantidade_original = len(avaliacoes)
            
            cliente["avaliacoes"] = [
                a for a in avaliacoes if a.get("id") != avaliacao_id
            ]
            
            if len(cliente["avaliacoes"]) < quantidade_original:
                _salvar_dados_json(clientes)
                return True
    
    return False
